"""Generate training data."""
import json
from collections import namedtuple
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from . import augmentations as aug

Sheet = namedtuple("Sheet", "subject_id image_file boxes types")


class LabelFinderData(Dataset):
    """Generate augmented training data."""

    def __init__(self, sheets: list[dict], image_dir: Path, augment=False):
        super().__init__()
        self.image_dir = image_dir
        self.sheets = sheets
        self.augment = augment

    def __len__(self):
        return len(self.sheets)

    def __getitem__(self, idx):
        sheet = self.sheets[idx]
        path = self.image_dir / sheet["image_file"]

        # labels = [sub.CLASS2INT[t] for t in sheet["merged_types"]]
        labels = [1] * len(sheet["merged_types"])

        boxes = torch.tensor(sheet["merged_boxes"], dtype=torch.float32)
        if boxes.shape[0] == 0:
            boxes = torch.empty((0, 4), dtype=torch.float32)

        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

        with Image.open(path) as image:
            image = image.convert("L")
            if self.augment:
                image = aug.random_blur(image)
                image = aug.random_color(image)
                image, boxes = aug.random_rescale(image, boxes)
            image = transforms.ToTensor()(image)

        target = {
            "image_id": torch.tensor([int(sheet["subject_id"])]),
            "boxes": boxes,
            "labels": torch.tensor(labels, dtype=torch.int64),
            "area": area,
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64),
        }

        return image, target

    @staticmethod
    def read_jsonl(jsonl: Path):
        """Read JSONL file as sheet data."""
        with open(jsonl) as f:
            return [json.loads(ln) for ln in f.readlines()]
