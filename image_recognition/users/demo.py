from numpy import asarray
from PIL import Image
from matplotlib import pyplot as plt

def read_image(image_path, method="PIL", rgb=True):
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

def detect_faces_in_image(image_array, detector):
    faces = detector.detect_faces(image_array)
    return faces

def extract_faces_from_image(image_array, detector, required_size=(224, 224)):
    faces = detector.detect_faces(image_array)

    face_images = []

    for face in faces:
        # extract the bounding box from the first face
        x1, y1, width, height = result['box']
        # bug fix
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        # extract the face
        face = image_array[y1:y2, x1:x2]
        # resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize(required_size)
        face_array = asarray(image)
        face_images.append(face_array)
  
        # # extract the bounding box from the requested face
        # x1, y1, width, height = face['box']
        # x2, y2 = x1 + width, y1 + height

        # # extract the face
        # face_boundary = image_array[y1:y2, x1:x2]

        # # resize pixels to the model size
        # face_image = Image.fromarray(face_boundary)
        # face_image = face_image.resize(required_size)
        # face_array = asarray(face_image)
        # face_images.append(face_array)

    return face_images

# load images and extract faces for all images in a directory
def load_faces(directory):
    all_faces = list()
    # enumerate files
    for filename in listdir(directory):
        # path
        path = os.path.join(directory, filename)
        image, pixels = read_image(path)
        # get face
        faces = extract_faces_from_image(pixels, detector)
        # store
        all_faces.extend(faces)
    return all_faces
 
# load a dataset that contains one subdir for each class that in turn contains images
def load_dataset(directory):
    X, y = list(), list()
    # enumerate folders, on per class
    for subdir in listdir(directory):
        # path
        path = os.path.join(directory, subdir)
  
        # skip any files that might be in the dir
        if not isdir(path):
            continue
        # load all faces in the subdirectory
        faces = load_faces(path)
        # create labels
        labels = [subdir for _ in range(len(faces))]
        # summarize progress
        print('>loaded %d examples for class: %s' % (len(faces), subdir))
        # store
        X.extend(faces)
        y.extend(labels)
    return asarray(X), asarray(y)