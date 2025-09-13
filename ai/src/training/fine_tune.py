import torch
from torch.nn import Module
from typing import Sequence

def freeze_layers(
    model: Module, 
    layer_names: Sequence[str]
) -> None:
    """
    Disables gradient updates for selected layers in a model.

    Iterates over named parameters and sets `requires_grad = False` for any
    parameter whose name starts with one of the specified prefixes.

    Parameters:
        model (Module): PyTorch model.
        layer_names (Sequence[str]): List of layer name prefixes to freeze.
    """
    for name, param in model.named_parameters():
        if any(name.startswith(layer) for layer in layer_names):
            param.requires_grad = False

def load_checkpoint(
    model: Module, 
    path: str
) -> Module:
    """
    Loads model weights from a checkpoint file.

    Loads a state dictionary from disk and applies it to the given model.

    Parameters:
        model (Module): PyTorch model to update.
        path (str): Path to the checkpoint file (.pt or .pth).

    Returns:
        Module: Model with loaded weights.
    """
    state = torch.load(path, map_location="cpu")
    model.load_state_dict(state)
    return model

def replace_head(
    model: Module, 
    new_head: Module
) -> Module:
    """
    Replaces the output head of a model.

    Assumes the model has a `.head` attribute and replaces it with the provided module.

    Parameters:
        model (Module): PyTorch model with a `.head` attribute.
        new_head (Module): New head module to attach.

    Returns:
        Module: Updated model with replaced head.
    """
    model.head = new_head
    return model
