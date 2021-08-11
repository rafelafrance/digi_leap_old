"""Generate training data."""

import json
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms import ToTensor

from digi_leap.subject import CLASS2INT


class FasterRcnnData(Dataset):
    """Generate augmented training data."""

    def __init__(self, subjects: list[dict], image_dir: Path):
        super().__init__()

        self.image_dir = image_dir
        self.subjects = subjects

    def __len__(self):
        return len(self.subjects)

    def __getitem__(self, idx):
        subject = self.subjects[idx]
        path = self.image_dir / subject["image_file"]
        image = Image.open(path).convert("L")
        image = ToTensor()(image)

        labels = [CLASS2INT[t] for t in subject["merged_types"]]

        boxes = torch.tensor(subject["merged_boxes"], dtype=torch.float32)
        if boxes.shape[0] == 0:
            boxes = torch.empty((0, 4), dtype=torch.float32)

        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

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
        """Read JSONL file."""
        with open(jsonl) as f:
            return [json.loads(ln) for ln in f.readlines()]
