Title: PyViz at SciPy 2019
Date: 2019-07-12
Modified: 2019-07-12
Category: PyViz
Tags: scipy
Slug: pyviz-scipy-bof-2019
Authors: James A. Bednar and Thomas Caswell
Summary: Discussion about PyViz landscape at SciPy 2019 BoF
Picture: images/pyviz_graph.png
​​

The Python Data Visualization Birds-of-a-Feather session at the scientific Python conference brought together a dozen different authors of Python packages for visualizing data. Each author was asked to state one thing that they found exciting right now about Python data viz from their own perspective, along with another issue that they found frustrating or that needs attention. Panelists then voted on a few issues brought up in the introductions, and answered a variety of questions from the audience. Our notes from the meeting are below for all those interested.
​
## Panelist introductions
​
**James A. Bednar (Panel, hvPlot, Datashader, Colorcet, GeoViews)** Intro and overview of python viz landscape and overview of the new [pyviz.org](https://pyviz.org) website, including live status of 60+ Python viz tools. Excited about dashboarding in Python -- now a real thing that other languages should be jealous of! Frustrated by interoperability issues, from trying to assemble various libraries to solve big problems.
​

**Thomas Caswell (Matplotlib/PyQtGraph)** Diversity in PyViz libraries shows wide usage across domains; diversity is a feature, not a bug. No perfect solution for every domain. PyQtgraph - great for high speed desktop but please don’t try to do web dashboarding with it. Matplotlib is mostly in maintenance and housekeeping mode at the moment, but starting to think of what Matplotlib 4 should look like. PyQtgraph being revived after being dormant for a while; moving to py3 only release.
​

**Jon Mease (Plotly)** Independent contractor, speaking for the Python interface. Excited about V4 of Plotly, new themes, having it run in more places, integration of seaborn-style high-level API. Frustrated by the fact that the choice of library is often dictated by what interface you use---cmd line, Spyder, Jupyter, etc.
​

**Madicken Munk (yt)** yt is trying to expand to other non-astronomy domains. Having a major release in the next year. Switching to external unit conversion system, from Nathan Goldbaum. Creating a domain context system to make it easier to integrate with new domains. Frustrating is that it is difficult to separate out domain-specific stuff. yt naming still very astro-specific, even though the functionality is largely domain agnostic. yt maintains Jupyter widget library built on rust compiled to WebAssembly.
​

**Josef Heinen (GR)** GR focuses on speed and transparency, used in Matplotlib but language agnostic, which is useful for scientists working with multiple languages. Can be integrated into QT, GTK, etc. Currently transpiling software into JS which will allow browser use and will enable matplotlib browser web backend. He personally prefers Julia.
​

**Jean-Luc Stevens (HoloViews)** HoloViews is a layer/API on top of other libraries (Matplotlib, Bokeh, Plotly). Focuses on exploratory work. Working on maturing, polishing, and further documenting the system, which is now used as a lower-level base for other libraries like hvPlot. Frustration - fragmented, quickly moving ecosystem makes integration difficult.
​

**David Hoese (VisPy)** Python wrapper around OpenGL. High level interface. Excited about improved number of contributors to VisPy. Frustrations 1. Platform support for OpenGL -- Apple has dropped OS X support! 2. Backwards compatibility concerns makes it difficult to maintain VisPy -- new features are hard to support without breaking support for older standards.
​

**Filipe Fernandes (Folium)** Folium is widely used, but is not a healthy project. Only use folium if you are already on it. Will be discontinued in 2-3 years. For new projects use alternatives, e.g. ipyleaflet.
​

**Thomas Robitaille (Glue)** Glue provides multidimensional analysis. Uses other packages for viz. Excited about Jupyter ecosystem to dashboards to desktop apps. Frustrated by the number of viz packages; not sure which to use and which to contribute missing functionality to. It’s, especially difficult when they all have such different governance models; it’s not always clear which ones you can have impact on, so it is difficult to invest in substantial efforts.
​

**Matthew McCormick (VTK)** Will update pyviz.org soon with more information. 2D/3D spatial viz. New version vtkjs supports WebGL. Provides volume rendering in the browser, now with Jupyter widgets. Would like to see - lots of progress in packaging, but need dashboarding tools and Qt and be able to create single-file applications using things like pyinstaller.
​

**Martin Renou (ipywidgets)** Pushing widget libraries outside of Python into C++. Also Voila library for dashboarding. Open issue if you are unable to convert notebook to dashboard.
​

**Julia Signell (Bokeh)** Exciting: very stable now, much nicer than it was a few years ago. Please try again if you previously found rough edges. Bokeh is not supported by only one company, with widely spread developers, NumFocus support, and a completely open model. Go to [discourse.bokeh.org](https://discourse.bokeh.org/) if you want to get involved.
​

**Brian Granger (Jupyter/Altair)** (based on Vega/Vegaliite). Excited about the impact seen of having a declarative viz grammar. Key lesson learned: start with data model and not the API. Enables building bindings for different languages, and offers lessons for other viz libs. Frustrating - packaging, not just Python and C, but JS is also involved. Really challenging issues. 
​

**Jake Vanderplas (pdVega, Altair)** Excited about the ongoing efforts in pandas to expand its plotting API to target backends beyond matplotlib ([pandas#14130](https://github.com/pandas-dev/pandas/issues/14130)).
​
​
## Votes

**Vote:** Raise your hand if your project is truly ready and willing to accept substantial community contributions. (All voted yes!)
​

**Vote:** Are there too many viz libraries? (2-5 voted yes, depending on caveats)
​
​
## Audience Questions:
​
**1. I work a lot in web dev; what is the state of PyViz libraries ability to make viz accessible?**
​

For dashboarding libraries like Voila and Panel, some aspects are currently only solved at the JS/HTML level, by using a responsive template that supports mobile devices, larger fonts for low vision, etc. Most of those issues have not been taken on by the Python packages directly. Even when using such a template, it is up to the users to use good colors, etc., though Colorcet and Viscm offer good colorblind-safe colormaps that can help. Textual summary of graphical representations is an open area. Guides to making viz accessible would be an excellent addition to PyViz.org. Suggestion from Marinna Martini: [www.w3.org/WAI](https://www.w3.org/WAI).
​

**2. What are good Python options for displaying real-time data from sensors?**
​

PyQtGraph was designed for this use case, providing high frame rates for many sensors. VisPy is also great for this, with examples in the repo for how to do this using various choices of backend. Bokeh Spectrogram example is good, though not quite as high performance as native GUI systems. GR is also an option, with examples in documentation. HoloViews has a streaming data guide and integrates with Streamz lib for easy plotting of streaming data sources, using Datashader when needed for large datasets. VTK based tools for images/point sets have fairly good support for real-time usage. Plotly.py with Dash and Matplotlib also have ways to do this.
​

**3. What support is available for Dask and CuPy data structures?**
​

VisPy has to convert to Numpy first. hvPlot works with Dask arrays and dataframes directly.
​

**4. Is there support for CMYK-safe colormaps, so that figures are perceptually uniform when printed, e.g. on conference posters?**
​

Not that anyone on the panel is aware.

​
**5. Is there anyone fighting against the emerging consensus around tidy dataframes as input structure, which is annoying in practice after investing in well-structured multi-indexes?**
​

hvPlot supports wide data formats, though not currently multi-indexes directly. Altair assumes a tidy dataframe. Altair only covers a small subset of viz space, with a complex SQL-like pipeline, and hence needs a constrained data format. Altair may need helper tools to convert to tidy formats. hvPlot is a good example of this approach; it’s a high-level wrapper that works well with wide (non-tidy) data formats, converting it to the tidy format expected by HoloViews.
​

**6.Will there be changes to backend for alternate display formats, etc. in Matplotlib?**
​

Short answer: yes. Long answer: still in planning stages. Better export paths are needed that are more semantic that can go to Bokeh and Altair etc. We need many more libraries that are wrappers on the main libraries. Building those helper libraries needs to be easy and simple to spin up.
