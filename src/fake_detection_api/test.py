import os
import cv2
import numpy as np
import argparse
import warnings
import time

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')

import ntpath


def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True


def truncate_float(value, digits_after_point=2):
    """
    Truncate long float numbers
    >>> truncate_float(1.1477784, 2)
       1.14
    """
    pow_10 = 10 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10


def verify_real(image, model_dir, device_id="0"):
    """
    Check is real face or spoofed face

    Args:
        image ([type]): image file or image array
        model_dir ([type]): [description]
        device_id (str, optional): [description]. Defaults to "0".
    """
    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()

    image_bbox = model_test.get_bbox(image)
    prediction = np.zeros((1, 3))
    test_speed = 0
    # sum the prediction from single model's result
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": image,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = image_cropper.crop(**param)
        start = time.time()
        prediction += model_test.predict(img, os.path.join(model_dir, model_name))
        test_speed += time.time()-start

    # draw result of prediction
    label = np.argmax(prediction)
    value = prediction[0][label] / 2

    print("label: {}".format(label))
    print("score: {:.2f}".format(value))
    print("image_bbox: {}".format(image_bbox))
    print("Prediction cost {:.2f} ms".format(test_speed))
    
    score = truncate_float(value, digits_after_point=3)

    return (label, score, image_bbox)


if __name__ == "__main__":
    print("\n")

    image_file="media/images/own_grady.jpg"
    image = cv2.imread(image_file)
    # result = check_image(image)
    # if result is False:
    #     return
    label, score, image_bbox = verify_real(image, model_dir="./resources/anti_spoof_models", device_id="0")
    
    if label == 1:
        print("Real Face. Score: {:.2f}.".format(score))
        result_text = "RealFace Score: {:.2f}".format(score)
        color = (255, 0, 0)
    else:
        print("Fake Face. Score: {:.2f}.".format(score))
        result_text = "FakeFace Score: {:.2f}".format(score)
        color = (0, 0, 255)

    print("\n")
    print(f"Face box: {image_bbox}")