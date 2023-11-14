# HoloViz Blog

This repo contains the HoloViz blog which is built on Quarto


## Authoring

Start by installing [Quarto](https://quarto.org/docs/get-started/).

The best way to get started with contributing to this repository is to copy the `/posts/template` folder and update its name as you wish. This folder contains:

- an `index.ipynb` file that is your blog notebook, it could also be a Markdown file. This file has a special header (must be a `raw` cell, or Markdown) that you must adapt.
- an `images` folder in which you should store all the images and assets you link from your post, e.g. `![](./images/example.png)`.
- a `repro` folder in which you should include anything that can help reproducing your post in the future, e.g. lock files.

From the repo root then run `quarto preview`, this command will build the site and open a tab in your browser to preview it, updates to the repo files are reflected live.

When you're ready to contribute a new blog post or an edit to the repository, open a PR and commit your file. If it's a notebook, commit it **evaluated**. The [dev website](https://holoviz-dev.github.io/blog-dev/) is re-built everytime
you push a commit to a PR, make sure your blog post looks as you expect. The [main site](https://blog.holoviz.org/) gets updated once the PR is merged.
