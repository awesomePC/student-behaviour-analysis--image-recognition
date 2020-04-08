import os, random
import gc # garbage collector

from PIL import Image, ImageFont, ImageDraw, ImageEnhance

from numpy import asarray
from numpy import expand_dims

from django.conf import settings

import tensorflow as tf
graph = tf.get_default_graph()

from keras.models import load_model # loading model
from keras import backend as K

from mtcnn.mtcnn import MTCNN


detector = MTCNN()

facenet_model_file = os.path.join(
    settings.MEDIA_ROOT, 'neural_models/facenet_keras.h5'
)
facenet_model = load_model(
    facenet_model_file, compile=False
)

fv_model_file = os.path.join(
    settings.MEDIA_ROOT, 'neural_models/face-verification-model.h5'
)
face_verification_model = load_model(
    fv_model_file, compile=False
)


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
        pixels = asarray(image)
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


def detect_faces_in_image(image_array):
    """
    Detect faces in image using MTCNN
    
    Args:
        image_array (numpy array): Image pixels
        detector (object): MTCNN face detector
    
    Returns:
        array: Numpy array of detected faces(ndarray)
    """
    detected_faces = detector.detect_faces(image_array)
    return detected_faces

def detect_extract_faces_from_image(image_array, required_size=(160, 160), convert_2_numpy=True):
    """
    Extract faces from image
    
    Args:
        image_array (array): Image pixels in numpy format
        detector (object): face detector object
        required_size (tuple, optional): Final image resolution. Defaults to (160, 160).
        convert_2_numpy (bool, optional): convert pil face image to numpy. Defaults to True.
    
    Returns:
        tuple: If convert_2_numpy flag set to true then it returns list of faces in numpy format 
              otherwise it returns faces in pillow format
    """
    detected_faces = detector.detect_faces(image_array)

    extracted_faces = []

    for face in detected_faces:
        # extract the bounding box from the first face
        x1, y1, width, height = face['box']
        # bug fix
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        # extract the face
        face_boundary = image_array[y1:y2, x1:x2]
        # resize pixels to the model size
        face_image = Image.fromarray(face_boundary)
        face_image = face_image.resize(required_size)
        if convert_2_numpy:
            face_array = asarray(face_image)
            extracted_faces.append(face_array)
        else:
            extracted_faces.append(face_image)

    return (detected_faces, extracted_faces)

def extract_save_face(src, dest):
    """
    Extract face from image and save
    
    Args:
        src (str): Source image file path
        dest (str): Dest image file path
    """
    filename, file_extension = os.path.splitext(src)

    image, pixels = read_image(src)

    _, extracted_faces = detect_extract_faces_from_image(pixels, convert_2_numpy=False)

    if extracted_faces:
        img_single_face = extracted_faces[0]
        # pillow write image
        img_single_face.save(dest)
        # print(f"saved face from {src}")
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
    # import pdb; pdb.set_trace()

    # K.clear_session()

    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # face_pixels.shape # (160, 160, 3)
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std

    # transform face into one sample
    samples = expand_dims(face_pixels, axis=0)

    global graph
    with graph.as_default():
        # make prediction to get embedding
        yhat = facenet_model.predict(samples)
        # yhat[0].shape # (128,)
        return yhat[0]

def get_faces_and_embeddings_by_img_path(img_path):
    """
    get the faces and embeddings
    
    Args:
        img_path (str): Image path
    Returns:
        tuple: Face embedding (Image may contains two or more persons)
    """
    pil_image, pixels = read_image(img_path)

    detected_faces, extracted_faces = detect_extract_faces_from_image(pixels)

    face_embeddings = []

    for extracted_face in extracted_faces:
        embedding = get_embedding(extracted_face)
        embedding_reshaped = embedding.reshape(-1, 1) # (128, 1)
        face_embeddings.append(embedding_reshaped)
    
    # garbage collector
    gc.collect()
    return (detected_faces, extracted_faces, face_embeddings)


def verify_face_matching(known_embedding, real_time_embedding, thresh=0.4):
    # convert to input format
    known_embedding_reshaped = known_embedding.reshape(1, 128, 1)
    real_time_embedding_reshaped = real_time_embedding.reshape(1, 128, 1)

    y_pred = face_verification_model.predict(
        [known_embedding_reshaped, real_time_embedding_reshaped]
    )
    # print(f"y_pred : {y_pred}")

    distance = y_pred[0][0] # matching_score

    probability = 1 - distance

    if distance <= thresh:
        # print('>Image is a Match (%.3f <= %.3f)' % (distance, thresh))
        is_matched = True
    else:
        # print('>Not matching (%.3f > %.3f)' % (distance, thresh))
        is_matched = False
    
    return (is_matched, probability, y_pred, distance)


def highlight_faces(pil_image, detected_faces, outline_color="red"):
    """
    Highlight faces using pillow
    
    Args:
        pil_image (object): PiL image object
        faces (array): Numpy array
        outline_color (str, optional): Border color. Defaults to "red".
    
    Returns:
        [type]: [description]
    """
    draw = ImageDraw.Draw(pil_image)
    # for each face, draw a rectangle based on coordinates
    for face in faces:
        x, y, width, height = face['box']
        rect_start = (x, y)
        rect_end = ((x + width), (y + height))
        draw.rectangle((rect_start, rect_end), outline=outline_color)
    return pil_image


def highlight_recognized_faces(pil_image, recognized_faces, outline_color="red", write_result_2_disk=False, res_file_name_with_path=None):
    """
    Highlight recognized faces using pillow
    
    Args:
        pil_image (object): PiL image object
        recognized_faces (array): recognized faces from array
        outline_color (str, optional): Border color. Defaults to "red".
    
    Returns:
        [type]: [description]
    """
    draw = ImageDraw.Draw(pil_image)
    # for each face, draw a rectangle based on coordinates
    for recognized_face in recognized_faces:
        name = recognized_face["name"]
        probability = recognized_face["probability"]

        x, y, width, height = recognized_face['box']
        rect_start = (x, y)
        rect_end = ((x + width), (y + height))
        draw.rectangle((rect_start, rect_end), outline=outline_color)

        # draw text
        # text = "{}: {:.2f}%".format(name, probability * 100)
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
