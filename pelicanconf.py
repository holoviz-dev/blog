#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'HoloViz Developers'
SITENAME = 'HoloViz Blog'
SITEURL = 'http://blog.holoviz.org'

PATH = 'content'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

LINKS = (('HoloViews.org', 'https://holoviews.org/'),
         ('Panel.holoviz.org', 'https://panel.holoviz.org/'),
         ('GeoViews.org', 'https://geoviews.org/'),
         ('PyViz.org', 'http://pyviz.org/'),)

GITHUB_ORG = 'holoviz'
GITHUB_REPO = 'blog'
TWITTER_USER = 'HoloViews'

DEFAULT_PAGINATION = 10

MARKUP = ('md', 'ipynb')

PLUGIN_PATHS = ['./plugins']
PLUGINS = ['ipynb.markup']

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

IGNORE_FILES = ['.ipynb_checkpoints']

STATIC_PATHS = ['images']
THEME = 'theme'

LOGO = 'images/logo.png'

IPYNB_USE_META_SUMMARY = True
IPYNB_EXPORT_TEMPLATE = "templates/hide_code.tpl"

READERS = {"html": None}
