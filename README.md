# ophiDIan

<div align="center">
    <img src="https://github.com/guardicode/ophidian/raw/main/images/mascot.png", width="300">
</div>

---

<div align="center">

[![PyPI version](https://badge.fury.io/py/ophidian.svg)](http://badge.fury.io/py/ophidian)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fguardicode%2Fophidian%2Fmain%2Fpyproject.toml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)
[![License](https://img.shields.io/pypi/l/ophidian)](https://img.shields.io/pypi/l/ophidian)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/guardicode/ophidian)](https://img.shields.io/github/issues-pr/guardicode/ophidian)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/guardicode/ophidian/branch/main/graph/badge.svg)](https://codecov.io/gh/guardicode/ophidian)

</div>

---
## Description

ophiDIan is a Dependency Injection (DI) container for Python. Unlike other DI
containers that utilize decorators or configuration files to accomplish their
goal, ophiDIan uses type hints to identify and resolve dependencies. In other
words, by using type hinting to resolve dependencies, ophiDIan avoids making
your components dependent upon the DI framework.

Ophidian follows the [Register, Resolve, Release (RRR)
pattern](https://blog.ploeh.dk/2010/09/29/TheRegisterResolveReleasepattern/).

## Installation

Install with `pip install ophidian`

## Tutorial
### Dependency definitions

For this tutorial, we'll use the following class definitions:

```python
from abc import ABC, abstractmethod


class AbstractA(ABC):
    @abstractmethod
    def do_something(self):
        pass


class AbstractB(ABC):
    @abstractmethod
    def do_something_else(self):
        pass


class DependencyA(AbstractA):
    def do_something(self):
        print(f"{id(self)}: I am dependency A")


class DependencyB(AbstractB):
    def __init__(self, name: str):
        self._name = name
    def do_something_else(self):
        print(f"{id(self)} My name is {self._name}")


class TestClass1:
    def __init__(self, a: AbstractA):
        self.a = a


class TestClass2:
    __test__ = False

    def __init__(self, b: AbstractB):
        self.b = b


class TestClass3:
    def __init__(self, a: AbstractA, b: AbstractB):
        self.a = a
        self.b = b
```

### RRR

The first step in the RRR pattern is to *R*egister dependencies. This can be
performed using either the `register()` or `register_instance()` methods. Next,
objects can be built by *R*esolving. Finally, when the dependency is no
longer needed, it can be *R*eleased.

```python
from ophidian import DIContainer

dependency_b_instance = DependencyB("Mike")

di_container = DIContainer()
di_container.register(AbstractA, DependencyA)
di_container.register_instance(AbstractB, dependency_b_instance)

test_class_1 = di_container.resolve(TestClass1)
test_class_2 = di_container.resolve(TestClass2)
test_class_3 = di_container.resolve(TestClass3)

assert id(test_class_1.a) != id(test_class_3.a)
assert id(test_class_2.b) == id(dependency_b_instance)
assert id(test_class_2.b) == id(test_class_3.b)
assert isinstance(test_class_1.a, AbstractA)
assert isinstance(test_class_1.a, DependencyA)
assert isinstance(test_class_2.b, AbstractB)
assert isinstance(test_class_2.b, DependencyB)

# Note: All dependencies will automatically be released when the `di_container`
#       instance is cleaned up by the garbage collector.
di_container.release(AbstractA)
di_container.release(AbstractB)
```

In the above example, the `DIContainer.register()` method is used tell the DI
container that components that depend upon `AbstractA` should be supplied a new
instance of the concrete class `DependencyA`. The
`DiContainer.register_instance()` method is used to tell the DI container that
all components that depend upon `AbstractB` should be supplied with the same
instance of `DependencyB`.

### Conventions

Conventions are mainly used to resolve primitive dependencies. For example, if
a component depends upon a file path for a configuration file passed as a
string, a convention can be registered to provide the dependency.

```python
from ophidian import DIContainer

class Configuration:
    def __init__(self, a: DependencyA, config_file_path: str):
        ...

di_container = DIContainer()
di_container.register(AbstractA, DependencyA)
di_container.register_convention(str, "config_file_path", "/tmp/my_config_file")

configuration = di_container.resolve(Configuration)

di_container.release(AbstractA)
di_container.release_convention(str, "config_file_path")
```

We wouldn't want to use `register()` or `register_instance()`, as we wouldn't
want all string dependencies to be resolved with the configuration file path.
Instead, the DI container is informed about an established "convention" within
the code: components that depend upon the configuration file path expect a
string parameter named "config_file_path". See [Primitive Dependencies by Mark
Seemann](https://blog.ploeh.dk/2012/07/02/PrimitiveDependencies/) for more
information about conventions.

## Documentation
### DIContainer

```python
class DIContainer()
```

A dependency injection (DI) container that uses type annotations to resolve and
inject dependencies.

#### \_\_init\_\_

```python
def __init__()
```

#### register

```python
@no_type_check
def register(interface: Type[T], concrete_type: Type[T])
```

Register a concrete `type` that satisfies a given interface.

:param interface: An interface or abstract base class that other classes depend
upon</br>
:param concrete_type: A `type` (class) that implements `interface`</br>
:raises TypeError: If `concrete_type` is not a class, or not a subclass of
`interface`


#### register\_instance

```python
@no_type_check
def register_instance(interface: Type[T], instance: T)
```

Register a concrete instance that satisfies a given interface.

:param interface: An interface or abstract base class that other classes depend
upon</br>
:param instance: An instance (object) of a `type` that implements
`interface`</br>
:raises TypeError: If `instance` is not an instance of `interface`


#### register\_convention

```python
@no_type_check
def register_convention(type_: Type[T], name: str, instance: T)
```

Register an instance as a convention

At times — particularly when dealing with primitive types — it can be useful to
define a convention for how dependencies should be resolved. For example, you
might want any class that specifies `hostname: str` in its constructor to
receive the hostname of the system it's running on. Registering a convention
allows you to assign an object instance to a type, name pair.

**Example:**

        class TestClass:
            def __init__(self, hostname: str):
                self.hostname = hostname

        di_container = DIContainer()
        di_container.register_convention(str, "hostname", "my_hostname.domain")

        test = di_container.resolve(TestClass)
        assert test.hostname == "my_hostname.domain"

:param type_: The `type` (class) of the dependency</br>
:param name: The name of the dependency parameter</br>
:param instance: An instance (object) of `type_` that will be injected into constructors
                 that specify `[name]: [type_]` as parameters

### Errors
#### UnresolvableDependencyError

```python
class UnresolvableDependencyError(ValueError):
```

Raised when one or more dependencies cannot be successfully resolved.

## Running the tests

Running the tests is as simple as `poetry install && poetry run pytest`
