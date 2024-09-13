# HoloViz Blog

This repository contains the HoloViz blog, which is built using [Quarto](https://quarto.org/).

## Installation

### Quarto

Begin by installing [Quarto](https://quarto.org/docs/get-started/):

```bash
conda create -n holoviz-blog -c conda-forge r-quarto perl
conda activate holoviz-blog
```

## Authoring

To contribute to this repository, start by copying the `/posts/template` folder and renaming it as desired. This folder includes:

- An `index.ipynb` file, which is your blog notebook. This can also be a Markdown file. The file must contain a special header (in a `raw` cell or Markdown format) that you need to customize.
- An `images` folder to store all images and assets linked from your post, e.g., `![](./images/example.png)`.
- A `repro` folder to include any materials that will help reproduce your post in the future, such as lock files.

From the repository root, run `quarto preview`. This command will build the site and open a tab in your browser for a live preview. Updates to the repository files will be reflected immediately.

When you're ready to contribute a new blog post or an edit, open a pull request (PR) and commit your files. If you're committing a notebook, ensure it is committed in its evaluated state. The [development site](https://holoviz-dev.github.io/blog-dev/) is rebuilt every time you push a commit to a PR. Check that your blog post appears as expected. The [main site](https://blog.holoviz.org/) will be updated once the PR is merged.
