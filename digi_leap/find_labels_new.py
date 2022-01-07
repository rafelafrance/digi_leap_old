# #!/usr/bin/env python3
# """Use a trained model to cut out labels on herbarium sheets."""
# import pytorch_lightning as pl
# import torchvision
# from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
#
# from .pylib import subject as sub
#
#
# class FastRCNN(pl.LightningModule):
#     """Change the pretrained model for out uses."""
#
#     def __init__(self):
#         super().__init__()
#         self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
#             pretrained=True
#         )
#         in_features = self.model.roi_heads.box_predictor.cls_score.in_features
#         self.model.roi_heads.box_predictor = FastRCNNPredictor(
#             in_features, num_classes=len(sub.CLASSES) + 1
#         )
#
#     def forward(self, x):
#         return self.model(x)
#
#     def training_step(self, batch, batch_idx):
#         x, y = batch
#         y_hat = self(x)
#
#
# if __name__ == "__main__":
#     model = FastRCNN()
#     trainer = pl.Trainer(fast_dev_run=True)
#     trainer.fit(model)
