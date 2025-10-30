"""
Utility module for constructing dataclass instances from raw dictionaries, primarily used in routing
and message-handling contexts where payloads need to be parsed into structured objects.

This module defines the `RouterUtils` class, which provides methods to:

- Resolve type annotations by stripping wrappers like `Optional` and `Union`.
- Recursively instantiate dataclasses from nested dictionaries, including support for lists of dataclasses.
- Construct multiple named dataclass instances from a shared input dictionary and return them as a `NamedTuple`.

These utilities are especially useful in systems where incoming data (e.g., from message queues or APIs)
must be validated and transformed into typed Python objects before being passed to business logic layers.

Classes:
    - RouterUtils: Contains helper methods for dataclass construction and type resolution.

Dependencies:
    - Python standard library: `dataclasses`, `typing`, `collections`
    - Project-specific: `DataclassType` from `api_okx_v1.src.infrastructure._types`

Example usage:
    utils = RouterUtils()
    dto = utils.construct(data, MyDTO)
    dtos = utils.construct_many_named(data, [UserDTO, AuthDTO])

Note:
    All target classes must be valid dataclass types. Type resolution handles nested structures and optional fields.
"""


from dataclasses import is_dataclass, fields
from typing import (
    Type, 
    Any,
    Dict, 
    Sequence, 
    NamedTuple, 
    Union
)
from typing import get_origin, get_args
from collections import namedtuple


from api_okx_v1.src.infrastructure._types import DataclassType

class RouterUtils:
    def _resolve_type(self, tp: Any) -> Any:
        """
        Resolves a type annotation by removing Optional and Union wrappers.
        Returns the underlying base type.

        Args:
            tp (Any): The original type annotation.

        Returns:
            Any: The resolved base type.
        """
        origin = get_origin(tp)
        args = get_args(tp)

        if origin is Union:
            non_none = [arg for arg in args if arg is not type(None)]
            return non_none[0] if non_none else Any
        return tp

    def construct(self, data: Dict[str, Any], cls: Type[DataclassType]) -> DataclassType:
        """
        Recursively constructs an instance of the given dataclass type from a dictionary.
        Supports nested dataclasses and lists of dataclasses.

        Args:
            cls (Type[DataclassType]): The dataclass type to instantiate.
            data (Dict[str, Any]): A dictionary containing field values.

        Returns:
            DataclassType: An instance of the specified dataclass.

        Raises:
            TypeError: If cls is not a dataclass type.
        """
        if not isinstance(cls, type) or not is_dataclass(cls):
            raise TypeError(f"{cls} must be a dataclass type, not an instance")

        init_data = {}
        for f in fields(cls):
            value = data.get(f.name)
            raw_type = f.type
            resolved_type = self._resolve_type(raw_type)
            origin = get_origin(resolved_type)
            args = get_args(resolved_type)

            if is_dataclass(resolved_type) and isinstance(value, dict):
                init_data[f.name] = self.construct(resolved_type, value)  # type: ignore

            elif origin is list and args and is_dataclass(args[0]) and isinstance(value, list):
                nested_type = args[0]
                init_data[f.name] = [self.construct(nested_type, item) for item in value]  # type: ignore

            else:
                init_data[f.name] = value

        return cls(**init_data)

    def construct_many_named(
        self,
        data: Dict[str, Any],
        classes: Sequence[Type[DataclassType]]
    ) -> NamedTuple:
        """
        Constructs multiple dataclass instances from a shared dictionary.
        Returns a named tuple with field names based on class names.

        Args:
            data (Dict[str, Any]): Dictionary of values.
            classes (Sequence[Type[DataclassType]]): List of dataclass types to instantiate.

        Returns:
            NamedTuple: Named tuple of constructed dataclass instances.

        Raises:
            TypeError: If any item in classes is not a dataclass type.
        """
        for cls in classes:
            if not isinstance(cls, type) or not is_dataclass(cls):
                raise TypeError(f"{cls} must be a dataclass type, not an instance")

        names = [cls.__name__ for cls in classes]
        NamedResult = namedtuple("ConstructedDataclasses", names)
        instances = [self.construct(data, cls) for cls in classes]
        return NamedResult(*instances)
