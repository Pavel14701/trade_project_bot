import torch
from torch.nn import Module
from typing import Sequence

def freeze_layers(model: Module, layer_names: Sequence[str]) -> None:
    for name, param in model.named_parameters():
        if any(name.startswith(layer) for layer in layer_names):
            param.requires_grad = False

def load_checkpoint(model: Module, path: str) -> Module:
    state = torch.load(path, map_location="cpu")
    model.load_state_dict(state)
    return model

def replace_head(model: Module, new_head: Module) -> Module:
    model.head = new_head
    return model
