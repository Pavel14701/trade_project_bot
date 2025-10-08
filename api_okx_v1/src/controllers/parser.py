from dataclasses import fields, is_dataclass
from typing import Type, Any, Dict, Sequence, Tuple, TypeVar

DataclassType = TypeVar("DataclassType")

def construct(
    cls: Type[DataclassType], 
    data: Dict[str, Any]
) -> DataclassType:
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not dataclass")
    init_data = {}
    for f in fields(cls):
        value = data.get(f.name)
        if is_dataclass(f.type) and isinstance(value, dict):
            init_data[f.name] = value
    return cls(**init_data)

def construct_many(
    data: Dict[str, Any], 
    classes: Sequence[Type[DataclassType]]
) -> Tuple[DataclassType, ...]:
    return tuple(construct(cls, data) for cls in classes)