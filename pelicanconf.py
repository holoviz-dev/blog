#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'PyViz Developers'
SITENAME = 'PyViz Blog'
SITEURL = 'http://blog.pyviz.org'

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
         ('GeoViews.org', 'https://geoviews.org/'),
         ('PyViz.org', 'http://pyviz.org/'),)

GITHUB_ORG = 'pyviz'
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

READERS = {"html": None}
