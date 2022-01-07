"""Manipulate images to help with the OCR process."""
import numpy as np
import torch
from numpy import typing as npt
from torch.utils.data import DataLoader
from tqdm import tqdm

from . import db
from . import label_finder_data as lfd


def profile_projection(image, axis: int = 1) -> npt.ArrayLike:
    """Get a profile projection of a binary image."""
    array = np.asarray(image).copy()

    array[array == 0] = 1
    array[array == 255] = 0

    proj = np.sum(array, axis=axis)
    return proj


def get_image_norm(database, classifier, split_run, batch_size=16, num_workers=4):
    """Get the mean and standard deviation of the image channels."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data = db.select_split(database, split_run, split="train")
    split = lfd.LabelFinderData(data, classifier)
    loader = DataLoader(split, batch_size=batch_size, num_workers=num_workers)

    # TODO: Has bad round-off error according to Numerical Recipes in C, 2d ed. p 613
    sum_, sq_sum, count = 0.0, 0.0, 0

    for images, _ in tqdm(loader):
        images = images.to(device)
        sum_ += torch.mean(images, dim=[0, 2, 3])
        sq_sum += torch.mean(images ** 2, dim=[0, 2, 3])
        count += 1

    mean = sum_ / count
    std = (sq_sum / count - mean ** 2) ** 0.5
    return mean, std
