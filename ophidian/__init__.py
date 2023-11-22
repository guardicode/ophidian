from warnings import warn

from .di_container import DIContainer, UnresolvableDependencyError

warn(
    "The `ophidian-di` package has been deprecated. Please use `ophidian` instead.",
    DeprecationWarning,
    stacklevel=2,
)
