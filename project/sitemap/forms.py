# -*- coding: utf-8 -*-
from django import forms

import urlparse


class SitemapForm(forms.Form):
    url = forms.URLField()
    changefreq = forms.ChoiceField(choices=(
        (u'', u' -- не указывать -- '),
        (u'always', u'always'),
        (u'hourly', u'hourly'),
        (u'daily', u'daily'),
        (u'weekly', u'weekly'),
        (u'monthly', u'monthly'),
        (u'yearly', u'yearly'),
        (u'never', u'never'),
    ), required=False)
    lastmod = forms.DateField(input_formats=['%d.%m.%Y'], required=False)

    def __init__(self, *args, **kwargs):
        super(SitemapForm, self).__init__(*args, **kwargs)
        self.fields['url'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['placeholder'] = 'http://'
        self.fields['url'].widget.attrs['value'] = 'http://stackoverflow.com/'

        self.fields['lastmod'].widget.attrs['placeholder'] = u'не указывать дату'

    def clean_url(self):
        url = self.cleaned_data['url']
        parsed = list(urlparse.urlparse(url))
        parsed[0] = parsed[0].lower()  # scheme
        parsed[1] = parsed[1].lower()  # netloc
        url = urlparse.ParseResult(*parsed).geturl()
        return url
