"""Use a trained model to cut out labels on herbarium sheets."""
import effdet
from effdet import DetBenchTrain
from effdet import EfficientDet
from effdet.config.model_config import efficientdet_model_param_dict
from effdet.efficientdet import HeadNet


def create_model(
    num_classes=1, image_size=512, name="tf_efficientnetv2_s", pretrained=True
):
    efficientdet_model_param_dict[name] = dict(
        name=name,
        backbone_name=name,
        backbone_args=dict(drop_path_rate=0.2),
        num_classes=num_classes,
        url="",
    )

    config = effdet.get_efficientdet_config(name)
    config.update({"num_classes": num_classes})
    config.update({"image_size": (image_size, image_size)})

    net = EfficientDet(config, pretrained_backbone=pretrained)
    net.class_net = HeadNet(config, num_outputs=num_classes)
    return DetBenchTrain(net, config)


# def get_model(num_classes=1, name="efficientdet_d0"):
#     config = effdet.get_efficientdet_config(name)
#     config.update({"num_classes": num_classes})
#
#     net = EfficientDet(config, pretrained_backbone=True)
#     net.class_net = HeadNet(config, num_outputs=num_classes)
#     return DetBenchTrain(net, config)
