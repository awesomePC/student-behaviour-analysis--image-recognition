import os
import cv2

from sklearn.preprocessing import LabelEncoder
import numpy as np

from tensorflow.keras.models import load_model

import operator

CKPT_DIR = "ckpt"

le_filename =  os.path.join(CKPT_DIR, "label_encoder_classes.npy")
labelencoder = LabelEncoder()
labelencoder.classes_ = np.load(le_filename)

model_file = os.path.join(CKPT_DIR, "inceptionresnetv2_model.best.hdf5")
inception_resnet_v2_model = load_model(model_file)


def truncate_float(value, digits_after_point=2):
    """
    Truncate long float numbers
    >>> truncate_float(1.1477784, 2)
       1.14
    """
    pow_10 = 10 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10

def test_single_image(model, img_single_face, normalize=True):

    if img_single_face.any():
        # vgg16 model requires normalized image
        # whereas resnet50, xception dosnot work properly on normalized image -- it may give wrong result if image is normalized
        if normalize:
            img_single_face = img_single_face.astype(float) / 255

        expanded_img_single_face = np.expand_dims(img_single_face, axis=0)
        pred = model.predict(expanded_img_single_face)

        # import pdb; pdb.set_trace()

        prob_result = [truncate_float(value, 3) for value in pred[0]]
        # get a dictionary of {'classname', 'probability'}
        prob_per_class_dict = dict(zip(labelencoder.classes_, prob_result))
        # print(f"\n prob_per_class_dict : {prob_per_class_dict}")
        
        # get max class name
        predicted_class = max(prob_per_class_dict.items(), key=operator.itemgetter(1))[0]
        # print(f'\n predicted_class : {predicted_class}')

        predicted_prob = prob_per_class_dict[predicted_class]
        # print(f'\n predicted probability : {predicted_prob}')

        return {
            'all_emotions': [
                {
                    'emotions': prob_per_class_dict,
                }
            ],
            'topmost_emotion': [predicted_class, predicted_prob]
        }
    else:
        print(f"Skipping.. No face found ")
        return {}


## testing
img_face = cv2.imread("media/cropped-faces/happy.png")

detected_emotions = test_single_image(inception_resnet_v2_model, img_face, normalize=False)
print(detected_emotions)