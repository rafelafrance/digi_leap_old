"""Generate training data."""
import warnings
from collections import namedtuple

import albumentations as A
import numpy as np
import torch
from albumentations.pytorch.transforms import ToTensorV2
from PIL import Image
from torch.utils.data import Dataset

from ... import consts

UnlabeledSheet = namedtuple("UnlabeledSheet", "path sheet_id")


class UnlabeledData(Dataset):
    def __init__(self, images: list[dict], image_size):
        super().__init__()
        self.image_size = image_size
        self.sheets: list[UnlabeledSheet] = self.build_sheets(images)
        self.transform = self.build_transforms(image_size)

    @staticmethod
    def build_sheets(ims) -> list[UnlabeledSheet]:
        """Group labels by sheet."""
        return [UnlabeledSheet(i["path"], torch.tensor([i["sheet_id"]])) for i in ims]

    def __len__(self):
        return len(self.sheets)

    def __getitem__(self, idx):
        sheet = self.sheets[idx]

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            with Image.open(consts.ROOT_DIR / sheet.path).convert("RGB") as image:
                sample = {
                    "image": np.asarray(image),
                    "bboxes": [[0, 0, 1, 1]],
                    "targets": [1],
                }
                sample = self.transform(**sample)
                boxes = np.array(sample["bboxes"])

                _, new_h, new_w = sample["image"].shape

                target = {
                    "bboxes": torch.tensor(boxes, dtype=torch.float32),
                    "labels": torch.tensor(sample["targets"]),
                    "image_id": torch.tensor([sheet.sheet_id]),
                    "img_size": (new_h, new_w),
                    "img_scale": torch.tensor([1.0]),
                }

        return sample["image"], target, sheet.sheet_id

    @staticmethod
    def build_transforms(image_size):
        xform = [
            A.Resize(width=image_size, height=image_size, p=1.0),
            A.Normalize(consts.IMAGENET_MEAN, consts.IMAGENET_STD_DEV),
            ToTensorV2(p=1.0),
        ]
        return A.Compose(
            xform,
            bbox_params=A.BboxParams(format="pascal_voc", label_fields=["targets"]),
        )
