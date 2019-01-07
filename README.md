# PyViz Blog

This repo contains the PyViz blog which is built on Pelican and Pelican-ipynb

## Authoring

1. Write a notebook preferable exporting the bokeh JS and matplotlib images to files
2. Embed the corresponding HTML to load the JS/image
3. Add a ``.ipynb-meta`` file like this:

```
Title: HoloViews 1.10 Release
Slug: release_1.10
Date: 04/24/2018
Category: release
Tags: holoviews
Author: Philipp Rudiger
Summary: Release announcement for HoloViews 1.10
Picture: images/collage.png
```

4. Build the website with ``make html``
5. Serve the website to localhost:8000 with ``make serve``
6. ``git commit`` the added materials

## Deployment

7. ``aws s3 sync ./output s3://blog.holoviews.org``
8. ``aws cloudfront create-invalidation --distribution-id E25L1RCMJ07CUF --paths "/*"``
