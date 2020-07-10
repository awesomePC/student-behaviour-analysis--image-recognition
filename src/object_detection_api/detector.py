import os
from enum import Enum

import numpy as np
import cv2
import imutils


class ObjectDetectorModels(Enum):

    MobileNetSSD        = 0    # MobileNetSSD caffe model
    YOLOv3              = 1    # yolo v3 -darkent framework
    RESNET50COCO        = 2    # resnet50 coco_best_v2.0.1
    DEFAULT = MobileNetSSD


class ObjectDetector:

    def __init__(self, model=ObjectDetectorModels.DEFAULT, path=None):
        self._base = None

        if model == ObjectDetectorModels.RESNET50COCO:
            self._base = ObjectDetector_RESNET50COCO(path)
        elif model == ObjectDetectorModels.YOLOv3:
            self._base = ObjectDetector_YOLOv3(path)
        elif model == ObjectDetectorModels.MobileNetSSD:
            self._base = ObjectDetector_MobileNetSSD(path)

    def detect(self, input_image_path):
        return self._base.detect(
            input_image_path
        )


class ObjectDetector_YOLOv3:
    def __init__(self, path):
        # self._detector = _detector
        pass

    def detect(self, input_image_path):
        import cvlib as cv
        from cvlib.object_detection import draw_bbox
        frame = cv2.imread(input_image_path)

        # new_size = (300, 300)
        # frame = cv2.resize(frame, new_size)

        bbox, label, conf = cv.detect_common_objects(frame, confidence=0.50, model='yolov3-tiny')
        # output_image = draw_bbox(frame, bbox, label, conf)
        # cv2.imwrite(output_image_path, output_image)
        return (bbox, label, conf)


class ObjectDetector_MobileNetSSD:
    def __init__(self, path):
        # initialize the list of class labels MobileNet SSD was trained to
        # detect, then generate a set of bounding box colors for each class
        self.CLASSES = self.get_classes(path)

        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self._detector = cv2.dnn.readNetFromCaffe(
            os.path.join(path, 'MobileNetSSD_deploy.prototxt.txt'), 
            os.path.join(path, 'MobileNetSSD_deploy.caffemodel')
        )

    def get_classes(self, path):
        file_coco = os.path.join(path, 'coco.names')
        with open(file_coco, "r") as f:
            excludeFileContent = list(filter(None, f.read().splitlines()))
            return excludeFileContent
        return []
        
    def visualize_objects(self, frame, detections, min_confidence=0.4):
        (h, w) = frame.shape[:2]
        detections_final = []

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > min_confidence:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(self.CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    self.COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)
                
                detections_final.append({
                    'name': self.CLASSES[idx],
                    'percentage_probability': confidence,
                    'box': box,
                })
        return (frame, detections_final)

    def detect(self, input_image_path):
        input_image = cv2.imread(input_image_path)

        input_image = imutils.resize(input_image, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = input_image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(input_image, (300, 300)),
            0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        self._detector.setInput(blob)
        detections = self._detector.forward()
        # output_image, detections_final = self.visualize_objects(input_image, detections)
        # cv2.imwrite(output_image_path, output_image)
        return detections_final


class ObjectDetector_RESNET50COCO:

    def __init__(self, path):
        from imageai.Detection import ObjectDetection
        self._detector = ObjectDetection()
        self._detector.setModelTypeAsRetinaNet()
        self._detector.setModelPath( os.path.join(path, 'resnet50_coco_best_v2.1.0.h5'))
        self._detector.loadModel()


    def detect(self, input_image_path):
        detections = self._detector.detectObjectsFromImage(
            input_image=input_image_path,
        )
        # for eachObject in detections:
        #     print(
        #         eachObject["name"] , " : " , 
        #         eachObject["percentage_probability"]
        #     ) 
        return detections


