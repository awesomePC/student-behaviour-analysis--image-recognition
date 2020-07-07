"""
This code is used to batch detect images in a folder.
"""
import os
import sys

import cv2

import time

import argparse
from types import SimpleNamespace # creating argparse manually

from detector import FaceDetectorModels, FaceDetector

from settings import MODEL_DIR

input_path = "static/imgs"
result_path = "static/detect_imgs_results"

detector_number = 6
face_detector_model = FaceDetectorModels(detector_number)
face_detector = FaceDetector(model=face_detector_model, path=MODEL_DIR)


if not os.path.exists(result_path):
    os.makedirs(result_path)
listdir = os.listdir(input_path)
sum = 0
for file_path in listdir:
    img_path = os.path.join(input_path, file_path)
    orig_image = cv2.imread(img_path)
    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
    
    start_time = time.time()
    detected_faces = face_detector.detect(image)
    print("--- %s seconds --- \n" % (time.time() - start_time))

    for detected_face in detected_faces:
        # import pdb;pdb.set_trace()
        x, y, x2, y2 = detected_face["box"]
        cv2.rectangle(orig_image, (x, y), (x2, y2), (0, 0, 255), 2)
        # print(f"confidence: {detected_face['confidence']}")
        # label = f"""{voc_dataset.class_names[labels[i]]}: {probs[i]:.2f}"""
        # label = f"{probs[i]:.2f}"
        # cv2.putText(orig_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(orig_image, str(len(detected_faces)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imwrite(os.path.join(result_path, file_path), orig_image)
    print(f"Found {len(detected_faces)} faces. The output image is {result_path}")
print(sum)
