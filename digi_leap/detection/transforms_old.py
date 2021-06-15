import numpy as np
import torch
from PIL import Image
from torch.nn import Module
from torchvision.transforms import InterpolationMode, functional as F, transforms as T


class Compose:
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image, target):
        for transform in self.transforms:
            image, target = transform(image, target)
        return image, target


class ToTensor(Module):
    def forward(self, image, target):
        image = F.to_tensor(image)
        return image, target


class RandomHorizontalFlip(T.RandomHorizontalFlip):
    def forward(self, image, target):
        if torch.rand(1) < self.p:
            width, _ = F._get_image_size(image)
            image = F.hflip(image)
            bbox = target['boxes']
            bbox[:, [0, 2]] = width - bbox[:, [2, 0]]
            target['boxes'] = bbox
        return image, target


class RandomVerticalFlip(T.RandomVerticalFlip):
    def forward(self, image, target):
        if torch.rand(1) < self.p:
            _, height = F._get_image_size(image)
            image = F.vflip(image)
            bbox = target['boxes']
            bbox[:, [1, 3]] = height - bbox[:, [3, 1]]
            target['boxes'] = bbox
        return image, target


class ColorJitter(Module):
    def __init__(
            self,
            brightness=(0.875, 1.125),
            contrast=(0.5, 1.5),
            hue=(-0.05, 0.05),
            saturation=(0.5, 1.5),
            p=0.5):
        super().__init__()
        self._brightness = T.ColorJitter(brightness=brightness)
        self._contrast = T.ColorJitter(contrast=contrast)
        self._hue = T.ColorJitter(hue=hue)
        self._saturation = T.ColorJitter(saturation=saturation)
        self.p = p

    def forward(self, image, target):
        if isinstance(image, torch.Tensor):
            if image.ndimension() not in {2, 3}:
                raise ValueError(
                    'image should be 2/3 dimensional. Got {} dimensions.'.format(
                        image.ndimension()))
            elif image.ndimension() == 2:
                image = image.unsqueeze(0)

        r = torch.rand(6)

        contrast_before = r[0] < 0.5

        if contrast_before and r[1] < self.p:
            image = self._contrast(image)

        if r[2] < self.p:
            image = self._brightness(image)

        if r[3] < self.p:
            image = self._hue(image)

        if r[4] < self.p:
            image = self._saturation(image)

        if not contrast_before and r[1] < self.p:
            image = self._contrast(image)

        if r[5] < self.p:
            channels = F._get_image_num_channels(image)
            permutation = torch.randperm(channels)

            is_pil = F._is_pil_image(image)
            if is_pil:
                image = F.to_tensor(image)
            image = image[..., permutation, :, :]
            if is_pil:
                image = F.to_pil_image(image)

        return image, target


class Resize(Module):
    def __init__(self, size, interpolation=InterpolationMode.BILINEAR, p=0.5):
        super().__init__()
        self._resize = T.Resize(size, interpolation=interpolation)
        self.p = p
        self.height, self.width = size

    def forward(self, image, target):
        image = self._resize(image)
        bbox = np.array(target['boxes'])
        height, width = image.shape[-2:]
        bbox[:, [0, 2]] *= self.width / width
        bbox[:, [1, 3]] *= self.height / height
        target['boxes'] = bbox
        return image, target
