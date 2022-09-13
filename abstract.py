from typing import List


class Abstract:
    """
    Custom implementation of abstract classes.

    Set the `__required_methods__` and `__required_methods__` in the base class.
    If they are missing in the child class, AttributeError is raised.
    """

    __required_methods__: List[str] = []
    __required_attributes__: List[str] = []

    def __init_subclass__(cls, **kwargs):
        if Abstract in cls.__bases__:
            return
        for name in cls.__required_attributes__:
            if not hasattr(cls, name):
                raise AttributeError(f'Missing attribute "{name}" in class "{cls}".')
        for name in cls.__required_methods__:
            if not hasattr(cls, name):
                raise AttributeError(f'Missing method "{name}" in class "{cls}".')
            if not callable(getattr(cls, name)):
                raise AttributeError(f'Attribute "{name}" in class "{cls}" should be a method.')
