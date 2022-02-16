"""Generate training data."""
import warnings
from collections import defaultdict
from collections import namedtuple

import albumentations as A
import numpy as np
import torch
from albumentations.pytorch.transforms import ToTensorV2
from PIL import Image
from PIL import ImageDraw
from PIL.Image import Image as ImageType
from torch.utils.data import Dataset
from torchvision import transforms

from digi_leap.pylib import const
from digi_leap.pylib import subject as sub

Sheet = namedtuple("Sheet", "path boxes targets subject_id")

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
IMAGE_SIZE = (512, 512)


class LabelFinderData(Dataset):
    """Generate augmented training data."""

    def __init__(self, labels: list[dict], augment=False):
        super().__init__()
        self.augment = augment
        self.sheets: list[Sheet] = self.build_sheets(labels)
        self.transform = self.build_transforms(augment)

    @staticmethod
    def build_sheets(labels) -> list[Sheet]:
        """Group labels by sheet."""
        old_sheets = defaultdict(lambda: defaultdict(list))
        for lb in labels:
            key = (lb["subject_id"], lb["path"])
            old_sheets[key]["targets"].append(sub.CLASS2INT[lb["class"]])
            old_sheets[key]["boxes"].append(
                [
                    lb["label_left"],
                    lb["label_top"],
                    lb["label_right"],
                    lb["label_bottom"],
                ]
            )

        new_sheets: list[Sheet] = []
        for (subject_id, path), value in old_sheets.items():
            new_sheets.append(
                Sheet(
                    path,
                    torch.tensor(value["boxes"], dtype=torch.float32),
                    torch.tensor(value["targets"], dtype=torch.float32),
                    torch.tensor([subject_id]),
                )
            )

        return new_sheets

    def __len__(self):
        return len(self.sheets)

    def __getitem__(self, idx):
        sheet = self.sheets[idx]

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            image = Image.open(const.ROOT_DIR / sheet.path).convert("RGB")
            sample = {
                "image": np.asarray(image),
                "bboxes": sheet.boxes,
                "targets": sheet.targets,
            }
            sample = self.transform(**sample)
            boxes = np.array(sample["bboxes"])

            _, new_h, new_w = image.shape
            boxes[:, [0, 1, 2, 3]] = boxes[:, [1, 0, 3, 2]]  # convert to y x y x

            target = {
                "bboxes": torch.tensor(boxes, dtype=torch.float32),
                "labels": torch.tensor(sample["targets"]),
                "image_id": torch.tensor([sheet.subject_id]),
                "image_size": (new_h, new_w),
                "image_scale": torch.tensor([1.0]),
            }

        return sample["image"], target, sheet.subject_id

    @staticmethod
    def build_transforms(augment=False):
        """Build a pipeline of image transforms specific to the dataset."""
        xform = [A.Resize(width=IMAGE_SIZE[0], height=IMAGE_SIZE[1], p=1.0)]

        if augment:
            xform += [
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.ShiftScaleRotate(p=0.5),
                A.RandomBrightnessContrast(p=0.3),
                A.RGBShift(r_shift_limit=30, g_shift_limit=30, b_shift_limit=30, p=0.3),
            ]

        xform += [
            A.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ToTensorV2(p=1.0),
        ]
        return A.Compose(
            xform,
            bbox_params=A.BboxParams(format="pascal_voc", label_fields=["targets"]),
        )

    @staticmethod
    def build_transforms_torch(augment=False):
        """Build a pipeline of image transforms specific to the dataset."""
        xform = [transforms.Resize(IMAGE_SIZE)]

        if augment:
            xform += [
                transforms.AutoAugment(),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
            ]

        xform += [
            transforms.ToTensor(),
            transforms.ConvertImageDtype(torch.float),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]

        return transforms.Compose(xform)

    def show_image(self, idx) -> ImageType:
        """Draw the boxes on the image."""
        sheet = self.sheets[idx]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            image = Image.open(const.ROOT_DIR / sheet.path).convert("RGB")
            draw = ImageDraw.Draw(image)

        for box in sheet.boxes.tolist():
            draw.rectangle(box, outline="red", width=4)

        return image
