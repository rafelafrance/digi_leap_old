"""Use a trained model to cut out labels on herbarium sheets."""
from argparse import Namespace

import effdet
from effdet import DetBenchTrain
from effdet import EfficientDet
from effdet.config.model_config import efficientdet_model_param_dict
from effdet.efficientdet import HeadNet


ArgsType = Namespace


def create_model(num_classes=1, image_size=512, backbone="tf_efficientnet_lite0"):
    """Build an EfficientDet model."""
    efficientdet_model_param_dict[backbone] = dict(
        name=backbone,
        backbone_name=backbone,
        backbone_args=dict(drop_path_rate=0.2),
        num_classes=num_classes,
        url="",
    )

    config = effdet.get_efficientdet_config(backbone)
    config.update({"num_classes": num_classes})
    config.update({"image_size": (image_size, image_size)})

    net = EfficientDet(config, pretrained_backbone=True)
    net.class_net = HeadNet(config, num_outputs=num_classes)
    return DetBenchTrain(net, config)
