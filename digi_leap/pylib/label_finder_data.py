"""Generate training data."""
import json
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from . import augmentations as aug


class FasterRcnnData(Dataset):
    """Generate augmented training data."""

    def __init__(self, subjects: list[dict], image_dir: Path, augment=False):
        super().__init__()
        self.image_dir = image_dir
        self.subjects = subjects
        self.augment = augment

    def __len__(self):
        return len(self.subjects)

    def __getitem__(self, idx):
        subject = self.subjects[idx]
        path = self.image_dir / subject["image_file"]

        # labels = [sub.CLASS2INT[t] for t in subject["merged_types"]]
        labels = [1] * len(subject["merged_types"])

        boxes = torch.tensor(subject["merged_boxes"], dtype=torch.float32)
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
            "image_id": torch.tensor([int(subject["subject_id"])]),
            "boxes": boxes,
            "labels": torch.tensor(labels, dtype=torch.int64),
            "area": area,
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64),
        }

        return image, target

    @staticmethod
    def read_jsonl(jsonl: Path):
        """Read JSONL file as subject data."""
        with open(jsonl) as f:
            return [json.loads(ln) for ln in f.readlines()]
