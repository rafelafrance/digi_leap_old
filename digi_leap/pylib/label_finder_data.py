"""Generate training data."""
import warnings
from collections import namedtuple

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from . import augmentations as aug
from . import subject as sub

# Bounding boxes are in pascal format: (x_min, y_min, x_max, y_max)
Sheet = namedtuple("Sheet", "path boxes labels subject_id")


class LabelFinderData(Dataset):
    """Generate augmented training data."""

    def __init__(self, sheets: list[dict], augment=False):
        super().__init__()
        self.augment = augment

        self.sheets: list[Sheet] = []
        for sheet in sheets:
            labels = [sub.CLASS2INT[t] for t in sheet["merged_types"]]
            self.sheets.append(
                Sheet(
                    sheet["path"],
                    torch.tensor(sheet["merged_boxes"], dtype=torch.float32),
                    torch.tensor(labels, dtype=torch.int64),
                    torch.tensor([int(sheet["subject_id"])]),
                )
            )

    def __len__(self):
        return len(self.sheets)

    def __getitem__(self, idx):
        sheet = self.sheets[idx]

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            with Image.open(sheet.path) as image:
                image = image.convert("L")
                if self.augment:
                    image = aug.random_blur(image)
                    image = aug.random_color(image)
                    image, boxes = aug.random_rescale(image, sheet.boxes)
                image = transforms.ToTensor()(image)

        return image, sheet.boxes, sheet.labels, sheet.subject_id
