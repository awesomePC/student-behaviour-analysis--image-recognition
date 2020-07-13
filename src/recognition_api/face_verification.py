
import os, random
import gc # garbage collector
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

import numpy as np

from keras.models import load_model # loading model

import io
import json

from settings import (
    DETECTOR_NUMBER,
    MODEL_DIR,
    
    facenet_model_file,
    face_verification_model_file,
)
import helpers

from detector import FaceDetectorModels, FaceDetector

from keras_vggface.utils import preprocess_input
from keras_vggface.vggface import VGGFace
from scipy.spatial.distance import cosine

face_detector = None
face_embedding_model = None
# face_verification_model = None

def init_face_detector():
    global face_detector
    model_detector = FaceDetectorModels(DETECTOR_NUMBER)
    face_detector = FaceDetector(model=model_detector, path=MODEL_DIR)
    # face_detector = MTCNN()
    return True

def load_models():
    """
    Load facenet and our own model
    """
    global face_embedding_model

    # create a vggface model object
    face_embedding_model = VGGFace(model='resnet50',
        include_top=False,
        input_shape=(224, 224, 3),
        pooling='avg'
    )
    return True


def read_image(image_path, method="PIL", rgb=True):
    """
    Read image from disk
    
    Args:
        image_path (str): Image path
        method (str, optional): which library to use. Defaults to "PIL".
        rgb (bool, optional): convert to rgb. Defaults to True.
    
    Returns:
        tuple: image_object, and image pixels in numpy format
    """
    if method == "PIL":
        # load image from file
        image = Image.open(image_path)
        if rgb:
            # convert to RGB, if needed
            image = image.convert('RGB')
        # convert to array
        # obtain_image_pixels
        pixels = np.asarray(image)
        return (image, pixels)
    elif method == "CV":
        print("Not implimented yet")
        return (False, False)
    elif method == "MATPLOT":
        print("Not implimented yet")
        return (False, False)
    else:
        print("Please select proper reading method")
        return (False, False)

def detect_faces(image_array):
    """
    Detect faces in image using MTCNN
    
    Args:
        image_array (numpy array): Image pixels
        face_detector (object): MTCNN face detector
    
    Returns:
        dict: Detected faces dictionary
    """
    # detected_faces = face_detector.detect_faces(image_array)
    detected_faces = face_detector.detect(image_array)
    return detected_faces


def extract_faces(image_array, detected_face_boxes, required_size=(224, 224), convert_2_numpy=True):
    """
    Extract faces from image
    
    Args:
        detected_face_boxes (list): detected face boxes
        face_detector (object): face detector object
        required_size (tuple, optional): Final image resolution. Defaults to (224, 224).
        convert_2_numpy (bool, optional): convert pil face image to numpy. Defaults to True.
    
    Returns:
        tuple: If convert_2_numpy flag set to true then it returns list of faces in numpy format 
              otherwise it returns faces in pillow format
    """
    extracted_faces = []

    for detected_face in detected_face_boxes:
        # extract the bounding box from the first face
        x1, y1, x2, y2 = detected_face
        # x1, y1 = abs(x1), abs(y1)

        # extract the face
        face_boundary = image_array[y1:y2, x1:x2]
        # resize pixels to the model size
        face_image = Image.fromarray(face_boundary)
        face_image = face_image.resize(required_size)
        if convert_2_numpy:
            face_array = np.asarray(face_image)
            extracted_faces.append(face_array)
        else:
            extracted_faces.append(face_image)

    return (detected_face_boxes, extracted_faces)

def detect_extract_faces(image_array, required_size=(224, 224), convert_2_numpy=True):
    """
    Detect and Extract faces from image
    
    Args:
        image_array (array): Image pixels in numpy format
        face_detector (object): face detector object
        required_size (tuple, optional): Final image resolution. Defaults to (224, 224).
        convert_2_numpy (bool, optional): convert pil face image to numpy. Defaults to True.
    
    Returns:
        tuple: If convert_2_numpy flag set to true then it returns list of faces in numpy format 
              otherwise it returns faces in pillow format
    """
    detected_face_boxes = face_detector.detect(image_array)

    return extract_faces(
        image_array,
        detected_face_boxes, 
        required_size=required_size, 
        convert_2_numpy=convert_2_numpy,
    )

def extract_save_face(src, dest):
    """
    Extract face from image and save
    
    Args:
        src (str): Source image file path
        dest (str): Dest image file path
    """
    filename, file_extension = os.path.splitext(src)

    image, pixels = read_image(src)

    _, extracted_faces = detect_extract_faces(
        pixels, convert_2_numpy=False
    )

    if extracted_faces:
        img_single_face = extracted_faces[0]
        img_single_face.save(dest)
        return True
    else:
        print(f"No face found in {src}")
        return False


def get_embedding(face_pixels):
    """
    get the face embedding for one face
    
    Args:
        model (object): Keras loaded model that extract features
        face_pixels (array): Image array in numpy format
    Returns:
        array: one dimensional feature vector
    """
    # # scale pixel values
    # face_pixels = face_pixels.astype('float32')
    # # face_pixels.shape # (224, 224, 3)
    # # standardize pixel values across channels (global)
    # mean, std = face_pixels.mean(), face_pixels.std()
    # face_pixels = (face_pixels - mean) / std
    # # transform face into one sample
    # samples = np.expand_dims(face_pixels, axis=0)
    # # make prediction to get embedding
    # yhat = facenet_model.predict(samples)
    # # yhat[0].shape # (128,)
    # return yhat[0]

    sample = np.asarray(face_pixels, 'float32')
    # prepare the data for the model
    sample = preprocess_input(sample, version=2)
    sample = np.expand_dims(sample, axis=0)
    # perform prediction
    return face_embedding_model.predict(sample)[0]


def get_faces_and_embeddings(image_array):
    """
    get the faces and embeddings
    
    Args:
        image_array (array): Numpy array
    Returns:
        tuple: Face embedding (Image may contains two or more persons)
    """
    detected_faces, extracted_faces = detect_extract_faces(
        image_array
    )

    face_embeddings = []

    for extracted_face in extracted_faces:
        embedding = get_embedding(extracted_face)
        embedding_reshaped = embedding.reshape(-1, 1) # (128, 1)
        face_embeddings.append(embedding_reshaped)
    
    # garbage collector
    gc.collect()
    return (detected_faces, extracted_faces, face_embeddings)


def verify_face_matching(known_embedding, real_time_embedding, thresh=0.40):
    """
    Compare and check is known embeding match to real time embedding
    
    Args:
        known_embedding (array): Face known embedding
        real_time_embedding (array): Face real time embedding
        thresh (float, optional): Threshold. Defaults to 0.22.
    
    Returns:
        tuple: tuple containing is_matched, probability, y_pred, distance
    """
    # # convert to input format
    # known_embedding_reshaped = known_embedding.reshape(1, 128, 1)
    # real_time_embedding_reshaped = real_time_embedding.reshape(1, 128, 1)

    # y_pred = face_verification_model.predict(
    #     [known_embedding_reshaped, real_time_embedding_reshaped]
    # )
    # # print(f"y_pred : {y_pred}")

    # distance = y_pred[0][0] # matching_score

    distance = cosine(known_embedding, real_time_embedding)

    probability = 1 - distance

    if distance <= thresh:
        is_matched = True
    else:
        is_matched = False
    
    return (is_matched, probability, [], distance)


def highlight_faces(pil_image, detected_faces, outline_color="red"):
    """
    Highlight faces using pillow
    
    Args:
        pil_image (object): PiL image object
        detected_faces (List): MTCNN face detection result
        outline_color (str, optional): Border color. Defaults to "red".
    
    Returns:
        pil: face highlighted image
    """
    draw = ImageDraw.Draw(pil_image)
    # for each face, draw a rectangle based on coordinates
    for face in detected_faces:
        x, y, x2, y2 = face
        rect_start = (x, y)
        rect_end = (x2, y2)
        draw.rectangle((rect_start, rect_end), outline=outline_color)
    return pil_image


def highlight_recognized_faces(pil_image, recognized_faces, outline_color="red", write_result_2_disk=False, res_file_name_with_path=None):
    """
    Highlight recognized faces using pillow
    for each face, draw a rectangle based on coordinates

    Args:
        pil_image (object): PiL image object
        recognized_faces (array): recognized faces from array
        outline_color (str, optional): Border color. Defaults to "red".
    
    Returns:
        pil: face highlighted image with labels
    """
    draw = ImageDraw.Draw(pil_image)

    for recognized_face in recognized_faces:
        name = recognized_face["name"]
        probability = recognized_face["probability"]
        if 'outline_color' in recognized_face:
            outline_color = recognized_face.get("outline_color")
            
        x, y, x2, y2 = recognized_face['box']
        rect_start = (x, y)
        rect_end = (x2, y2)
        draw.rectangle(
            (rect_start, rect_end), outline=outline_color
        )

        text = f"{name}: { round(probability * 100, 2) }"

        text_y_cordinate = y - 10 if y - 10 > 10 else y + 10

        draw.text(
            (x, text_y_cordinate), # co-ordinates
            text, # text
            (255, 255, 255) # text color # (255, 255, 255) white
        )
    
    if write_result_2_disk:
        pil_image.save(res_file_name_with_path)
    return pil_image
