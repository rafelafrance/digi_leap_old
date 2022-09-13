"""Common utilities for building models."""
import logging

import torch
from torchvision.models import detection

from ... import consts
from ..models import efficient_det_model as edm


def load_model_state(model, load_model):
    model.state = torch.load(load_model) if load_model else {}
    if model.state.get("model_state"):
        logging.info("Loading a model.")
        model.load_state_dict(model.state["model_state"])


def tf_efficientnetv2_s(args):
    model = edm.create_model(
        len(consts.CLASSES), name=args.model, image_size=args.image_size
    )
    return model


def fasterrcnn_resnet50_fpn(_):
    model = detection.fasterrcnn_resnet50_fpn(pretrained=True)
    return model


def fasterrcnn_resnet50_fpn_v2(_):
    model = detection.fasterrcnn_resnet50_fpn(pretrained=True)
    return model


MODELS = {
    "tf_efficientnetv2_s": tf_efficientnetv2_s,
    "fasterrcnn_resnet50_fpn": fasterrcnn_resnet50_fpn,
    "fasterrcnn_resnet50_fpn_v2": fasterrcnn_resnet50_fpn_v2,
}
