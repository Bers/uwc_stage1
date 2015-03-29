# -*- coding: utf-8 -*-
from django.views.generic import FormView, TemplateView
from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages

from project.sitemap.crawler import SiteCrawler
from project.sitemap.forms import SitemapForm

from django_rq import job

import uuid
import redis


CACHE_TTL = 86400


@job
def crawl(result_key, url):
    crawler = SiteCrawler(result_key, url)
    crawler.parse_site()


class RedisMixin(object):

    def dispatch(self, *args, **kwargs):
        self.redis = redis.StrictRedis()
        return super(RedisMixin, self).dispatch(*args, **kwargs)


class Index(RedisMixin, FormView):
    permanent = False
    template_name = 'sitemap/index.html'
    form_class = SitemapForm

    def form_valid(self, form):
        result_key = uuid.uuid4().hex
        self.redis.hset(result_key, 'status', 'loading')
        self.redis.hset(result_key, 'url', form.cleaned_data['url'])
        self.redis.expire(result_key, CACHE_TTL)
        crawl.delay(result_key, form.cleaned_data)
        return redirect('status', result_key)

    def form_invalid(self, form):
        response = super(Index, self).form_invalid(form)
        response.context_data['error'] = 'Вы ввеле неверные данные'
        return response


class Status(RedisMixin, TemplateView):
    template_name = 'sitemap/status.html'

    def get(self, *args, **kwargs):
        result_key = self.kwargs['result_key']
        self.result = self.redis.hgetall(result_key)
        if self.result:
            if self.result['status'] == 'done':
                return redirect('result', result_key)
            return super(Status, self).get(*args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):
        context = super(Status, self).get_context_data(**kwargs)
        if 'links' in self.result:
            self.result['links'] = int(self.result['links'])
        context['result'] = self.result
        return context


class Result(RedisMixin, TemplateView):
    template_name = 'sitemap/result.html'

    def get_context_data(self, **kwargs):
        context = super(Result, self).get_context_data(**kwargs)
        result = self.redis.hgetall(self.kwargs['result_key'])

        if result.get('status') != 'done':
            raise Http404

        if 'links' in result:
            result['links'] = int(result['links'])
        if 'elapsed' in result:
            result['elapsed'] = int(result['elapsed'])
        context['result'] = result
        return context
