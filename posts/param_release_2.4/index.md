---
title: "Param 2.4.0 Release"
date: "2026-05-21"
description: "Release announcement for Param 2.4.0, introducing full typing support"
author: "Philipp Rudiger"
categories: [release, param]
image: "images/param_typing.png"
aliases:
  - ../../param_2.4.html
---

## What is Param?

[Param](https://param.holoviz.org/) is an open-source Python library that lets you define classes with strongly typed, validated parameters. It is the foundation of the [HoloViz](https://holoviz.org) ecosystem, powering Panel, hvPlot, HoloViews, and many other libraries. Param handles runtime validation, serialization, and dependency tracking so you can focus on the logic of your application rather than on boilerplate data-checking code.

## New Release!

We are excited to announce the 2.4.0 release of Param! This release brings first-class static typing support to Param, a long-awaited improvement that makes the entire Param-based ecosystem significantly easier to use in modern Python development environments.

- [**Full typing support**](#full-typing-support): Parameters now carry precise type information that flows through to IDE autocompletion, inline documentation, and static analysis tools.
- [**Type inference from constructor arguments**](#type-inference-from-constructor-arguments): Types are inferred not just from the Parameter subclass, but also from keyword arguments like `allow_None`, `item_type`, and `class_`.
- [**Four type checkers tested**](#type-checker-compatibility): Param is now verified against `mypy`, `pyright`, `pyrefly`, and `ty` in CI.
- [**py.typed marker**](#pytyped-marker): The `py.typed` PEP 561 marker is now included, signaling to tools that Param ships its own type annotations.
- [**Limitations and workarounds**](#limitations): Known limitations with `Selector` and `Literal` types, and how to work around them today.
- [**Future direction**](#future-direction): A preview of annotation-first parameter declarations coming in Param 3.0.

Many thanks to the contributors to this release.

<hr>

You can install the latest version of Param with `conda install param`, `pip install param`, or `uv add param`.

<hr>

## Full Typing Support

Param 2.4.0 introduces comprehensive static typing support, making `Parameterized` classes significantly more useful in modern development workflows. If you use VSCode (via Pylance), PyCharm, or any other editor with a Python language server, you will now get accurate autocompletion, inline documentation, and type-error highlighting for all Param-based code, including the entire HoloViz ecosystem built on top of it.

Before this release, Param's parameters were effectively untyped from a static analysis perspective. A value like `slider.value` would be inferred as `Any`, meaning your type checker could not help you catch bugs where the wrong type was passed or returned. With 2.4.0, types flow through correctly:

```python
import param

class Model(param.Parameterized):
    threshold = param.Number(default=0.5)
    name_ = param.String(default="unnamed")
    count = param.Integer(allow_None=True)

m = Model()

# Your IDE now knows these types precisely:
reveal_type(m.threshold)  # float | int
reveal_type(m.name_)      # str
reveal_type(m.count)      # int | None
```

Note that this typing support currently applies to parameter *access* on instances. The `Parameterized` constructor (`__init__`) does not yet benefit from per-parameter type narrowing, so keyword arguments passed at instantiation time are not statically checked. This is a known limitation that will be addressed in a future release.

This change is, of course, well overdue but it represents a first step towards modernizing not just Param but the entire HoloViz ecosystem.

## Type Inference from Constructor Arguments

The core design decision in Param's typing approach is that types are inferred from the *Parameter declaration*, not from a separate type annotation. This means the same constructor call you already write for runtime validation also communicates intent to your type checker.

The inference works at two levels:

1. **The Parameter subclass** determines the base type. `param.String` implies `str`, `param.Integer` implies `int`, `param.Number` implies `int | float`, and so on.
2. **Keyword arguments** refine the type further. `allow_None=True` adds `None` to the union. `item_type=str` on a `List` narrows the element type. `class_=MyModel` on a `ClassSelector` pins the type to `MyModel`.

```python
import param
import typing as t
from typing import Any
from typing_extensions import assert_type

class MyModel:
    pass

class Example(param.Parameterized):
    title = param.String()
    retries = param.Integer(allow_None=False)
    timeout = param.Number(allow_None=True)
    tags = param.List(item_type=str)
    model = param.ClassSelector(class_=MyModel, allow_None=False, default=MyModel())
    optional_model = param.ClassSelector(class_=MyModel, allow_None=True, default=None)

e = Example()

assert_type(e.title, str)
assert_type(e.retries, int)
assert_type(e.timeout, int | float | None)
assert_type(e.tags, list[str])
assert_type(e.model, MyModel)
assert_type(e.optional_model, MyModel | None)
```

Under the hood, this works through Python's overload mechanism. `Parameter` is now a generic class — `Parameter[_T]` — and each subclass defines `@overload` signatures that perform type narrowing based on the keyword arguments present in the call. This is purely a static analysis mechanism: no runtime behavior changes.

### The `allow_None` Pattern

The `allow_None` argument deserves special attention because it is the most common way to control nullability. The inference rules are consistent:

| Declaration | Inferred type |
|---|---|
| `param.Integer()` | `int` |
| `param.Integer(default=None)` | `int \| None` |
| `param.Integer(allow_None=False)` | `int` |
| `param.Integer(allow_None=True)` | `int \| None` |
| `param.Number()` | `int \| float` |
| `param.Number(allow_None=True)` | `int \| float \| None` |
| `param.String()` | `str` |
| `param.String(allow_None=True)` | `str \| None` |

The default for `allow_None` varies by Parameter subclass, so when in doubt, be explicit. Being explicit about `allow_None` also serves as useful documentation for anyone reading your class definition.

### `List` with `item_type`

A `param.List` without `item_type` is inferred as `list[Any]`. Providing `item_type` narrows the element type:

```python
class Config(param.Parameterized):
    labels = param.List(item_type=str)
    weights = param.List(item_type=float)
    callbacks = param.List()  # list[Any]

c = Config()
assert_type(c.labels, list[str])
assert_type(c.weights, list[float])
```

### `ClassSelector` with `class_`

For `ClassSelector`, the `class_` argument determines the inferred type. Combined with `allow_None`, it cleanly expresses optional object references:

```python
class Engine(param.Parameterized):
    pass

class Pipeline(param.Parameterized):
    engine = param.ClassSelector(class_=Engine, allow_None=False, default=Engine())
    fallback = param.ClassSelector(class_=Engine, allow_None=True, default=None)

p = Pipeline()
assert_type(p.engine, Engine)
assert_type(p.fallback, Engine | None)
```

## py.typed Marker

Param 2.4.0 ships a `py.typed` marker file in the `param` package, as specified in [PEP 561](https://peps.python.org/pep-0561/). This signals to type checkers and build tools that Param provides its own inline type annotations and no separate type stubs are needed.

## Type Checker Compatibility

Python's type checking ecosystem has matured considerably and now includes several competing tools with different strengths. Param 2.4.0 is verified against four of them in CI:

**pyright** is Microsoft's type checker, which powers the Pylance language server in VSCode. It is the **primary target for Param's type annotations**. If you or your users develop in VSCode, correct inference will surface automatically without any extra configuration.

**mypy** is the original Python type checker and remains the most widely used, particularly in CI pipelines. Param passes mypy's strict checking.

**pyrefly** is a new type checker from Meta, written in Rust and still in beta. It ships its own language server and is focused on performance at scale.

**ty** is a new type checker from the Astral team (the authors of `ruff` and `uv`), also written in Rust and still in beta.

If you are developing a library built on Param, the recommendation is to use pyright as your primary type checker. Param's annotations are optimized for pyright first, and since it is the checker most users encounter implicitly through their editor, correct inference there benefits the widest audience.

## Mypy Plugin

If you use mypy, we recommend enabling the param mypy plugin. Add the following to your `pyproject.toml`:

```toml
[tool.mypy]
plugins = ["param.mypy_plugin"]
```

Or in `mypy.ini` / `setup.cfg`:

```ini
[mypy]
plugins = param.mypy_plugin
```

The plugin is needed because param uses a metaclass `__setattr__` to route class-level parameter assignment through the descriptor protocol. Without the plugin, mypy does not recognize this pattern ([mypy #9758](https://github.com/python/mypy/issues/9758)) and rejects valid code like:

```python
class MyModel(param.Parameterized):
    flag = param.Boolean(default=False)

MyModel.flag = True  # mypy error without the plugin
```

With the plugin enabled, mypy correctly understands that the assignment sets the parameter's default value and type-checks it against the parameter's value type. Pyright handles this correctly without any plugin.

## Limitations

Type narrowing in Python's type system has real limits, and it is worth being honest about what Param's typing cannot do today.

### `Selector` and `Literal` Types

The most significant limitation involves `Selector` parameters with a fixed set of objects. Ideally, `param.Selector(objects=["train", "eval"])` would infer `Literal["train", "eval"]`. Unfortunately, Python's type system does not currently support narrowing a generic type parameter based on the runtime *values* of a list argument, only based on the *types* of arguments.

As a result, `Selector` currently infers `Any`:

```python
class TrainingConfig(param.Parameterized):
    mode = param.Selector(objects=["train", "eval"])

config = TrainingConfig()
reveal_type(config.mode)  # Any
```

The workaround is to add a redundant explicit annotation with a `type: ignore` comment to suppress the assignment type mismatch:

```python
from typing import Literal

class TrainingConfig(param.Parameterized):
    mode: Literal["train", "eval"] = param.Selector(
        objects=["train", "eval"]
    )  # type: ignore[assignment]

config = TrainingConfig()
reveal_type(config.mode)  # Literal["train", "eval"]
```

This is not elegant, and it is one of the reasons the typing story for Param is not finished with this release.

## Future Direction

The typing approach in 2.4.0, inferring types from constructor arguments, is a significant improvement over the untyped state before it, but it has an inherent ceiling. The overload-based narrowing cannot express everything a developer might want to communicate.

The next step is annotation-first parameter declarations, which is being prototyped in [PR #1133](https://github.com/holoviz/param/pull/1133) and is planned for Param 3.0. The idea is to allow defining parameters using standard Python type annotations, similar to how dataclasses and Pydantic models work:

```python
# Future Param 3.0 style (prototype, not yet released)
class Model(param.ParamModel):
    threshold: float = 3.5
    mode: Literal["train", "eval"] = "train"
    tags: list[str] = []
```

In this model, the type annotation is the source of truth for static analysis, and Param uses it to configure the parameter's runtime behavior. This eliminates the `Selector`/`Literal` workaround, removes the need for overloads in Param's internals, and aligns Param with the conventions that Python developers already know from dataclasses and Pydantic.

The migration path from the current style to this new style is designed to be straightforward, so existing code will continue to work.

## Practical Recommendations

If you are updating an existing Param-based codebase to take advantage of the new typing, here is what we recommend:

- Use specific Parameter subclasses (`Integer`, `String`, `ClassSelector`, etc.) instead of the base `Parameter` class wherever possible. The more specific the subclass, the better the inferred type.
- Set `allow_None` explicitly on parameters where nullability matters. This improves both runtime safety and the precision of the inferred type.
- For `List` parameters, provide `item_type` whenever the list is homogeneous. This is good practice regardless of typing, since it adds a free runtime validation.
- For `Selector` parameters with a known fixed set of values, add an explicit `Literal` annotation with `type: ignore[assignment]` for now. This is a temporary workaround until Param 3.0.

Run pyright alongside your tests. It is the checker most likely to benefit your users if you are building a library on top of Param, and catching type errors at development time is meaningfully cheaper than catching them at runtime.

## Changelog

For the full list of changes, see the [Param 2.4.0 changelog](https://github.com/holoviz/param/releases/tag/v2.4.0).

### 🚀 Features
* Make `Parameter` generic (`Parameter[_T]`) and add overloads for type narrowing
* Add `py.typed` PEP 561 marker to the `param` package
* Add type inference for `allow_None`, `item_type`, `class_`, and `bounds` constructor arguments
* Add `tests/assert_types.py` with `assert_type()` assertions verified in CI
* Add CI jobs for `mypy`, `pyright`, `pyrefly`, and `ty`

### 🔧 Maintenance
* Change `UndefinedType` sentinel from a custom class instance to an `enum.Enum` member for improved compatibility with type checkers