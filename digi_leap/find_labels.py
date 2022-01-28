#!/usr/bin/env python3
"""Use a trained model to cut out labels on herbarium sheets."""
from torch import nn


class LabelFinderModel(nn.Module):
    """Change the pretrained model for out uses."""

    # def __init__(self):
    #     super().__init__()
    #     self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
    #         pretrained=True
    #     )
    #     in_features = self.model.roi_heads.box_predictor.cls_score.in_features
    #     self.model.roi_heads.box_predictor = FastRCNNPredictor(
    #         in_features, num_classes=len(sub.CLASSES) + 1
    #     )
    #
    # def forward(self, x):
    #     return self.model(x)


def main():
    """Find labels on a herbarium sheet."""
    # model = FastRCNN()
    # trainer = pl.Trainer(fast_dev_run=True)
    # trainer.fit(model)


if __name__ == "__main__":
    main()
