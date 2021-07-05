#!/usr/bin/env python
"""Try training a detectron2 model."""

# import torch
# import torchvision
# import detectron2
# import numpy as np
# import os
# import json
# import cv2
# import random
# from detectron2.utils.logger import setup_logger
# from detectron2 import model_zoo
# from detectron2.engine import DefaultPredictor
# from detectron2.config import get_cfg
# from detectron2.utils.visualizer import Visualizer
# from detectron2.data import MetadataCatalog, DatasetCatalog
# from PIL import Image
# from google.colab.patches import cv2_imshow


# setup_logger()

# im = cv2.imread("./data/input.jpg")
# cfg = get_cfg()
# cfg.merge_from_file(
#     model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
# cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
#     "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
# predictor = DefaultPredictor(cfg)
# outputs = predictor(im)

# print(outputs["instances"].pred_classes)
# print(outputs["instances"].pred_boxes)

# v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
# out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
# image = Image.fromarray(out.get_image()[:, :, ::-1])
# image.show()
