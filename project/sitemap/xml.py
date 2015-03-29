from django.conf import settings

from lxml import etree

import datetime
import uuid
import os


def make_url(page):
    url_child = etree.Element('url')

    element = etree.Element('loc')
    element.text = page['loc']
    url_child.append(element)

    if page.get('lastmod'):
        element = etree.Element('lastmod')
        element.text = page['lastmod']
        url_child.append(element)

    if page.get('changefreq'):
        element = etree.Element('changefreq')
        element.text = page['changefreq']
        url_child.append(element)

    return url_child


def generate_xml(pages):
    root = etree.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    [root.append(make_url(page)) for page in pages]
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def make_sitemap(pages):
    result = generate_xml(pages)

    path = '%s/%s/sitemap.xml' % (
        datetime.date.today(),
        uuid.uuid4().hex
    )

    abs_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(os.path.dirname(abs_path)):
        os.makedirs(os.path.dirname(abs_path))
    with open(abs_path, 'w') as f:
        f.write(result)

    return path
