# -*- coding: utf-8 -*-
from project.sitemap.xml import make_sitemap

from urlparse import urlparse, urljoin
from lxml import html

from threading import Thread
from Queue import Queue

import requests
import eventlet
eventlet.monkey_patch()

import redis
import time
import re


class SiteCrawler(object):
    WORKERS = 10
    MAX_DEPTH = 10
    MAX_PAGES = 500
    MAX_CALLS = 600
    MAX_PAGESIZE = 500000  # bytes
    REQUEST_TIMEOUT = 3  # sec

    def __init__(self, result_key, data):
        self.redis = redis.StrictRedis()
        self.time_start = time.time()

        self.result_key = result_key
        self.user_url = data['url']
        self.lastmod = str(data['lastmod'] or '')
        self.changefreq = data['changefreq']

        parsed_url = urlparse(self.user_url)
        self.url_prefix = '%s://%s' % (
            parsed_url.scheme,
            parsed_url.netloc
        )
        self.scheme = parsed_url.scheme
        self.domain = parsed_url.netloc

        # отобранные для sitemap страницы
        self.pages = set()

        # обработанные адреса
        self.parsed = set()

    def set_progress(self):
        self.redis.hset(self.result_key, 'links', len(self.pages))

    def set_result(self, file_url):
        self.redis.hset(self.result_key, 'status', 'done')
        self.redis.hset(self.result_key, 'file_url', file_url)
        self.redis.hset(self.result_key, 'elapsed', int(time.time() - self.time_start))

    def parse_site(self):
        def worker():
            while True:
                url, depth = self.q.get()
                self.save_page(url, depth)
                self.q.task_done()

        self.q = Queue()
        for i in range(self.WORKERS):
            t = Thread(target=worker)
            t.daemon = True
            t.start()

        self.q.put((self.user_url, 0))

        self.q.join()

        self.save_results()

    def save_page(self, url, depth=0):
        '''
        обработка и сохранение страницы
        '''
        # не проверяли ли url ранее
        if url in self.parsed:
            return
        self.parsed.add(url)

        # лимиты
        if len(self.parsed) >= self.MAX_CALLS:
            return

        if len(self.pages) >= self.MAX_PAGES:
            return

        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT, stream=True)
        except Exception as e:
            print e
            return

        dom = self.get_dom(response)
        if dom is None:
            return

        self.pages.add(url)
        self.set_progress()

        if depth < self.MAX_DEPTH:
            self.process_page(url, dom, depth)

    def get_dom(self, response):
        # check content type
        ctype = response.headers.get('content-type')
        if ctype and not ctype.startswith('text/html'):
            print 'not html', response.url
            return

        # check response size
        clength = response.headers.get('content-length')
        if clength and int(clength) > self.MAX_PAGESIZE:
            print 'too big', response.url
            return

        try:
            with eventlet.Timeout(self.REQUEST_TIMEOUT, False):
                return html.fromstring(response.content)
        except Exception as e:
            print e
            return

    def process_page(self, page_url, dom, depth):
        '''
        разбираем ссылки с обрабатываемой страницы
        '''
        base_url = self.get_base_href(page_url, dom)

        hrefs = [a.get('href') for a in dom.cssselect('a[href]') if a.get('href')]
        hrefs = [self.format_href(base_url, h) for h in hrefs]
        hrefs = filter(lambda x: urlparse(x)[:2] == (self.scheme, self.domain), hrefs)  # same domain and scheme check
        [self.q.put((h, depth + 1)) for h in hrefs]
        return len(list(hrefs))

    def get_base_href(self, base_url, dom):
        base_path = urlparse(base_url).path

        # tag more important
        base_tags = dom.cssselect('base')
        if base_tags:
            if base_tags[0].get('href'):
                base_path = base_tags[0].get('href')

        return urljoin('%s://%s' % (self.scheme, self.domain), base_path)

    def format_href(self, base_url, href):
        # remove fragments like #var
        href = href.strip()
        href = re.sub('#.*$', '', href) or '/'

        # use base url
        if not href.startswith('/'):
            href = urljoin(base_url, href)

        # //blogspot.com/blog/ -> http://blogspot.com/blog/
        if href.startswith('//'):
            # schemeless
            href = u'%s:%s' % (
                self.scheme,
                href
            )

        # http://blogspot.com -> http://blogspot.com/
        if href.lower().startswith(('http://', 'https://')):
            if not urlparse(href).path:
                return '%s/' % href
        else:
            # relative
            href = u'%s://%s%s' % (
                self.scheme,
                self.domain,
                href
            )
        return href

    def save_results(self):
        pages = list(self.pages)
        pages = sorted(pages, key=lambda x: len(x))
        pages = [{
            'loc': url,
            'lastmod': self.lastmod,
            'changefreq': self.changefreq
        } for url in pages]

        file_url = make_sitemap(pages)

        self.set_result(file_url)
