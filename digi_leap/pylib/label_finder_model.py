"""Use a trained model to cut out labels on herbarium sheets."""
from effdet import DetBenchTrain
from effdet import EfficientDet
from effdet import get_efficientdet_config
from effdet.config.model_config import efficientdet_model_param_dict
from effdet.efficientdet import HeadNet


def create_model(num_classes=1, image_size=512, architecture="tf_efficientnetv2_l"):
    """Create and register an EfficientDet model."""
    efficientdet_model_param_dict["tf_efficientnetv2_l"] = dict(
        name="tf_efficientnetv2_l",
        backbone_name="tf_efficientnetv2_l",
        backbone_args=dict(drop_path_rate=0.2),
        num_classes=num_classes,
        url="",
    )

    config = get_efficientdet_config(architecture)
    config.update({"num_classes": num_classes})
    config.update({"image_size": (image_size, image_size)})

    print(config)

    net = EfficientDet(config, pretrained_backbone=True)
    net.class_net = HeadNet(
        config,
        num_outputs=config.num_classes,
    )
    return DetBenchTrain(net, config)
