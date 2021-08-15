"""Common label augmentations for model training."""

import random

from PIL import ImageFilter
from torchvision import transforms


def random_blur(image, threshold=0.25):
    """Randomly blur the image."""
    if random.random() < threshold:
        return image
    radius = random.choice([1, 2])
    image = image.filter(ImageFilter.BoxBlur(radius=radius))
    return image


def random_color(image, threshold=0.1):
    "Random color jitter."
    if random.random() < threshold:
        return image
    image = transforms.ColorJitter(
        brightness=(0.5, 2.0),
        contrast=(0.5, 2.0),
        saturation=(0.5, 2.0),
        hue=(-0.25, 0.25),
    )(image)
    return image


def random_rescale(image, boxes, threshold=0.25):
    """Randomly rescale the image."""
    if random.random() < threshold:
        return image

    scale = random.choice([0.9, 0.8, 0.7])
    w, h = image.size
    w, h = round(w * scale), round(h * scale)
    image = image.resize((w, h))

    boxes[:, 0] *= scale
    boxes[:, 1] *= scale
    boxes[:, 2] *= scale
    boxes[:, 3] *= scale

    return image, boxes
