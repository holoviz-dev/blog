---
title: "HoloViz Examples Gallery Modernization"
date: "2024-12-11"
description: "Announcement of the modernized version of the HoloViz examples gallery, a curated collection of domain-specific narrative examples using various HoloViz projects."
author:
  - Junshen Tao
  - Isaiah Akorita
  - Demetris Roumis
  - Maxime Liquet
categories: "announcement"
image: "images/thumbnail.jpg"
---

[HoloViz](https://holoviz.org){.external target="_blank"} is an ecosystem of open-source tools designed to make data visualization in Python both simpler and more powerful, featuring projects like [Panel](https://panel.holoviz.org){.external target="_blank"}, [hvPlot](https://hvplot.holoviz.org){.external target="_blank"}, [HoloViews](https://holoviews.org){.external target="_blank"}, and [Datashader](https://datashader.org){.external target="_blank"}. The individual galleries for these tools (such as the [Panel App Gallery](https://panel.holoviz.org/gallery/index.html){.external target="_blank"} or the [HoloViews Gallery](https://holoviews.org/gallery/index.html){.external target="_blank"}) primarily focus on demonstrating the specific capabilities and APIs of each package. In contrast, the [HoloViz Examples Gallery](https://examples.holoviz.org/){.external target="_blank"} takes a broader approach, showcasing over 40 **domain-specific narrative examples** that integrate multiple HoloViz tools. These examples are structured around real-world data stories, providing better context for both the analysis and the tools involved, while highlighting the power of cross-package workflows.

Beyond being a learning resource, the HoloViz Examples Gallery serves as an ideal onramp for new contributors to the ecosystem. It invites users to bring their domain expertise and create new examples that showcase their unique perspectives and use cases. With the combination of updated examples, contributor guides, and a streamlined process for adding new content, the gallery lowers barriers to entry for those interested in contributing to HoloViz, fostering a more diverse community. 

In this blog post, we’re excited to share significant improvements to the Examples Gallery, made possible by a [NumFocus](https://numfocus.org/){.external target="_blank"} small development grant.

[![](./images/holoviz_examples_gallery.jpg)](https://examples.holoviz.org){.external target="_blank"}

This website presents some unique features:

- Each example is available for download as an `anaconda-project`[^1] zip file, enabling users to run any example with the correct dependencies and datasets on any platform. Learn more about the process [here](https://examples.holoviz.org/getting_started.html#run-locally){.external target="_blank"}.
- Most of the examples have either a read-only Notebook deployment ([try one!](https://world-cup-notebook.holoviz-demo.anaconda.com/notebooks/world_cup.ipynb){.external target="_blank"}) or a fully interactive Panel app deployment ([try one!](https://world-cup.holoviz-demo.anaconda.com/){.external target="_blank"}). These deployments allow users to explore plots and apps interactively, even when full interactivity isn’t available on the static Examples website. Thanks to [Anaconda](https://www.anaconda.com/){.external target="_blank"} for providing us with this platform 🙏.

Maintaining a large collection of complex data visualization projects is challenging for an open-source team. Over time, the gallery's content, infrastructure, and design became outdated, with many examples depending on tools and APIs no longer aligned with best practices. While infrastructure updates were manageable, refreshing the content proved far more difficult. To address this, we applied for a [NumFocus Small Development Grant](https://numfocus.org/programs/small-development-grants){.external target="_blank"} in late 2022, aiming to modernize the gallery and onboard new contributors.

With the $10,000 grant awarded in early 2023, two new contributors, [Isaiah](https://github.com/azaya89){.external target="_blank"} and [Jason](https://github.com/jtao1){.external target="_blank"}, joined the project. Together, they worked toward the following goals:

- Update high-priority examples to reflect current best practices
- Improve and clarify guidelines for new contributors
- Organize examples into categories to enhance website navigation
- Add new examples to address underrepresented domains

With the help of a [comprehensive checklist](https://github.com/holoviz-topics/examples/wiki/Example-Modernization-Checklist-(2024)){.external target="_blank"}, Jason and Isaiah, guided primarily by Demetris and Maxime with additional feedback from the HoloViz team, worked on updating the examples and successfully delivered [15 modernized examples](https://github.com/holoviz-topics/examples/pulls?q=is%3Apr+label%3A%22NF+SDG%22+){.external target="_blank"}. Their work spanned many areas, including restructuring examples, enhancing UI, updating dependencies, and adopting modern APIs. While their contributions are too extensive to cover fully in this post, we’ll focus on the improvements to API usage in the next section.

## Modernization: APIs

### [Plotting: prefer hvPlot over HoloViews when possible](https://holoviz.org/learn/background.html){.external target="_blank"}

Many examples were authored before hvPlot was created or when it wasn't yet mature enough to be used. hvPlot provides a simple plotting interface that is familiar to Pandas and Xarray users, while exposing many of the capabilities offered by the HoloViz tools. In many cases, we found out that it was possible to replace HoloViews code with more approachable hvPlot code. Of course, hvPlot cannot and should not replace all HoloViews code, for example, setting up more complex interactivity (e.g. linked selections, streams) is still only reserved to HoloViews.

For instance, the [NYC Taxi example](https://examples.holoviz.org/gallery/nyc_taxi/index.html){.external target="_blank"} creates a scatter plot to see the relationship between distance and fare cost.

Original code:
```python
scatter = hv.Scatter(samples, 'trip_distance', 'fare_amount')
labelled = scatter.redim.label(trip_distance="Distance, miles", fare_amount="Fare, $") 
labelled.redim.range(trip_distance=(0, 20), fare_amount=(0, 40)).opts(size=5)
```

Modernized code:
```python
samples.hvplot.scatter(
    'trip_distance', 'fare_amount', xlabel='Distance, miles',
    ylabel='Fare, $', xlim=(0, 20), ylim=(0, 40), s=5,
)
```

![](./images/hvplot_nyc_taxi.png)


### Large data: prefer `rasterize` over `datashade` when plotting with Bokeh

`rasterize` and `datashade` are HoloViews operations that leverage Datashader to transform an element into an image, each pixel's value being an aggregate of the data it contains. Applying these operations is extremely useful, and is in fact often the only way, to display very large datasets. However, these two operations work pretty differently. `datashade` sends to the front-end (your browser) an RGB image that is displayed by Bokeh as is, and, that's it, there's no more information about the data that can be exposed to you in the plot (e.g. via hover). On the other hand, `rasterize` sends a multidimensional array of the aggregated data, that Bokeh has then to transform (e.g. colormap). This is more work for Bokeh in the front-end, but also means that more information can be exposed in the plot! The machinery required to get `rasterize` to work well for many different cases through the whole stack (Bokeh, Datashader, HoloViews, hvPlot) is still work in progress but has reached a state where `rasterize` has become the recommended practice over `datashade`.

The animation shows a plot of the [NYC Taxi example](https://examples.holoviz.org/gallery/nyc_taxi/nyc_taxi.html#million-point-datashaded-plots-interactive){.external target="_blank"} that is built using `rasterize` to display 10 million data points. It displays the dropoff location, aggregating the points with the per-pixel sum of passenger count, information that is also made available on hover.

Modernized code: 
```python
df.hvplot.points(
    'dropoff_x', 'dropoff_y', rasterize=True, dynspread=True,
    aggregator=ds.sum('passenger_count'), cnorm='eq_hist', cmap=cc.fire[100:],
    xaxis=None, yaxis=None, width=900, height=500, bgcolor='black',
)
```

![](./images/nyc_taxi_rasterize.gif)


### [Interactivity: prefer `pn.bind()`](https://panel.holoviz.org/tutorials/basic/pn_bind.html){.external target="_blank"}

Over the years Panel has gained [a few APIs](https://panel.holoviz.org/explanation/index.html#apis){.external target="_blank"} and picking one is not always easy. For apps implemented using `param.Parameterized` classes, the best choice is usually to decorate methods with `@param.depends()`, and sometimes resort to `.param.watch()` for more fine-grained control. Outside of this scenario, `pn.bind()` is the preferred option over `pn.interact()` (deprecated), `@pn.depends()`, or `.param.watch()` (that can also sometimes be used). The [Portfolio Optimizer example](https://examples.holoviz.org/gallery/portfolio_optimizer/portfolio_optimizer.html#all-optimal-portfolios-efficient-frontier){.external target="_blank"} was updated using the new-ish [reactive expression API (`.rx`)](https://panel.holoviz.org/tutorials/basic/pn_rx.html){.external target="_blank"} that extends `pn.bind()` in many ways. It's a promising interface that is still somewhat experimental, we encourage users to try it out and provide feedback.


In the [Attractors example](https://examples.holoviz.org/gallery/attractors/clifford_panel.html){.external target="_blank"}, we replaced calling the deprecated (and very limiting) `pn.interact()` with a more explicit call to `pn.bind()`, linking various widgets to a function plotting an attractor with Datashader.

Original code:
```python
pn.interact(clifford_plot, n=(1,20000000), colormap=ps)
```

Modernized code: 
```python
widgets = {
    'a': pn.widgets.FloatSlider(value=1.9, end=2.0, step=0.1, name='a'),
    'b': pn.widgets.FloatSlider(value=1.9, end=2.0, step=0.1, name='b'),
    'c': pn.widgets.FloatSlider(value=1.9, end=2.0, step=0.1, name='c'),
    'd': pn.widgets.FloatSlider(value=0.8, end=1.0, step=0.1, name='d'),
    'n': pn.widgets.IntSlider(value=10000000, start=1000, end=20000000, step=100, name='n'),
    'colormap': pn.widgets.Select(value=ps['bmw'], options=ps, name='colormap'),
}

bound_clifford_plot = pn.bind(clifford_plot, **widgets)
pn.Column(*widgets.values(), bound_clifford_plot)
```

![](./images/bind_attractors.png)

## Improved contributor guide

The contributor guide was updated to reflect the changes made to the infrastructure and improved to guide new users through the journey of contributing a new example. Isaiah produced a step-by-step video explaining this process.

{{< video https://www.youtube.com/embed/r-9MF0sx_nA?si=QwXi45VNYDm5kOZR >}}

## New example: FIFA World Cup 2018

Isaiah, motivated by his passion for football (soccer), worked hard to contribute an example analyzing a dataset of the FIFA World Cup 2018 tournament. To learn more about the performances of players like Kylian Mbappe or Lionel Messi during the event, [visit the example's page](https://examples.holoviz.org/gallery/world_cup/world_cup.html){.external target="_blank"}, [run its notebook live](https://world-cup-notebook.holoviz-demo.anaconda.com/notebooks/world_cup.ipynb){.external target="_blank"}, or [visit its Panel app](https://world-cup.holoviz-demo.anaconda.com/world_cup){.external target="_blank"}.

[![](./images/fifa.png)](https://examples.holoviz.org/gallery/world_cup/world_cup.html)


## Feedback

### [Jason’s](https://github.com/jtao1){.external target="_blank"} reflections

Contributing to the revitalization of the examples website was an enlightening experience for me. Beyond learning about HoloViz tools, I gained a deeper understanding of open source contributions, including the workflow intricacies. This includes creating pull requests when making new changes or opening a new issue to document bugs found in the examples. Neither of which I’ve used when developing my own projects. Setting up the environment was also a tricky process as I had to do it in WSL. This exposure to WSL has helped me when working with other projects that are required to be using Linux. 

Overall, I am thankful to have been given this experience as a contributor as I’ve acquired a fundamental understanding of the tools that could be used.

### [Isaiah’s](https://github.com/Azaya89){.external target="_blank"} reflections

Working on this project has not only been an enjoyable experience but also an incredibly educational one. The journey began with a steep learning curve, but overcoming those initial challenges has made the entire process more rewarding.

**Key Learnings**

*Panel and HoloViz Libraries*

The Panel and HoloViz libraries were at the core of our project. Panel, being a high-level app and dashboarding solution for Python, allowed us to create interactive visualizations effortlessly. HoloViz, with its suite of tools designed to work seamlessly together, made data visualization tasks more intuitive and efficient. These tools have significantly enhanced my ability to create compelling and interactive data visualizations.

*Datashader*

Modernizing examples using the Datashader library was one of the highlights of the project. Datashader excels at creating meaningful visualizations from large datasets, a critical capability in the age of big data. My extensive use of Datashader has turned it into a reliable tool that I now feel confident using for future projects.

*Anaconda-Project*

Another crucial aspect of the project was mastering anaconda-project. It facilitated managing project dependencies and environments, ensuring that the project was reproducible at various levels. This experience underscored the [importance of reproducibility in data science](https://www.anaconda.com/blog/8-levels-of-reproducibility), which is vital for collaboration and long-term project sustainability.

**Overcoming Challenges**

The initial phase was riddled with challenges, particularly in setting up the project locally and navigating the submission process for Pull Requests. The support from the project leaders was invaluable. Their guidance helped streamline our workflow, making subsequent tasks more manageable and efficient. This collaborative effort not only improved my technical skills but also reinforced the importance of teamwork and effective communication.

**Future Prospects**

This project has been a significant milestone in my career. Working with the HoloViz team has not only broadened my technical expertise but also inspired me to continue exploring and utilizing these tools. I am excited to integrate HoloViz and its associated libraries into my future personal and professional data science endeavors.

This project has been an enriching experience, providing both challenges and opportunities for growth. The skills and knowledge gained will undoubtedly influence my future work, and I am grateful for the chance to contribute to such a dynamic and innovative project.

### Demetris and Maxime's reflections

TODO: @droumis adapt as you wish :) !

We want to thank Jason and Isaiah for all the hard work they put into this project. HoloViz, with all its libraries, and spread documentation, isn't an easy ecosystem to grasp in such a short time, but, by proactively asking questions, they have managed to accomplish an excellent job. Besides modernizing a ton of examples, their work has also allowed to highlight various regressions and gaps in the APIs, their fresh perspective has led to many UX discussions, all of which helping us improve the HoloViz tools. Thank you so much 🙂!

[^1]: `anaconda-project` is a project management tool created in 2016 and that predates most (if not all!) of the tools of this type like Poetry, Hatch, PDM,  Pixi, conda-project, etc. It is no longer maintained and we do not recommend adopting it, some day we'll migrate to another tool.