# Consuming the Keras REST API programmatically

# import the necessary packages
import os
import requests
from urllib.parse import urljoin
import json
from PIL import Image

import helpers
import settings

# initialize the Keras REST API endpoint URL along with the input
# image path
BASE_API_URL = "http://localhost:5001/"


def test_api_get_face_count(image_path):
    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    FACE_CNT_API_URL = urljoin(BASE_API_URL, '/get-face-count')

    # submit the request
    response = requests.post(
        FACE_CNT_API_URL, files=payload
    ).json()

    return response


def test_api_highlight_faces(image_path):
    from matplotlib import pyplot as plt

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    FACE_HIGHTLIGHT_API_URL = urljoin(BASE_API_URL, '/hightlight-faces')

    # submit the request
    response = requests.post(
        FACE_HIGHTLIGHT_API_URL, files=payload
    ).json()

    # # ensure the request was successful
    if response["success"]:
        encoded_img = response["encoded_img"]
        np_image_array = helpers.base64_to_pil(encoded_img)
        
        # show
        plt.imshow(np_image_array, interpolation='nearest')
        plt.show()
    else:
        print("Request failed")


def test_api_extract_faces_and_embeddings(image_path):
    from matplotlib import pyplot as plt
    from numpy import asarray, savetxt

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    payload = {
        "image": image
    }

    FACE_EXTRACTION_API_URL = urljoin(BASE_API_URL, '/extract-faces-and-embeddings')

    # submit the request
    response = requests.post(
        FACE_EXTRACTION_API_URL, files=payload
    ).json()

    # # ensure the request was successful
    if response["success"]:
        detected_faces = response['detected_faces']
        print(f"detected_faces : {detected_faces}")

        extracted_faces = response['extracted_faces']

        face_embeddings = response['face_embeddings']
        if face_embeddings:
            first_face_embedding = asarray(face_embeddings[0])
            
            file_single_face_embedding = os.path.join(
                settings.MEDIA_ROOT, 'face_embedding/single_face_embedding.txt'
            )
            # save one embeddings
            savetxt(file_single_face_embedding, first_face_embedding.view(float))

        return (detected_faces, extracted_faces)
    else:
        return ([], [])
        print("Request failed")


def test_api_compare_face_embedding(known_embedding, realtime_embedding):
    from numpy import asarray, loadtxt

    # convert to bytes
    bytes_known_embedding = known_embedding.tobytes()

    # convert to bytes
    bytes_realtime_embedding = realtime_embedding.tobytes()

    payload = {
        "known_embedding": bytes_known_embedding,
        "realtime_embedding": bytes_realtime_embedding
    }

    COMPARE_FACE_EMBEDDING_API_URL = urljoin(
        BASE_API_URL, '/compare-face-embedding'
    )

    # submit the request
    response = requests.post(
        COMPARE_FACE_EMBEDDING_API_URL, files=payload
    ).json()

    # # ensure the request was successful
    if response["success"]:
        print(response)
        return response
    else:
        print("Request failed")
        return False


def test_api_match_known_face_embedding(np_array_known_embedding, image_path):
    from matplotlib import pyplot as plt
    from numpy import asarray, loadtxt

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()
    # print(type(image))

    # convert to bytes
    known_embedding = np_array_known_embedding.tobytes()

    payload = {
        "image": image,
        "known_embedding": known_embedding
    }

    MATCH_FACE_EMBEDDING_API_URL = urljoin(
        BASE_API_URL, '/match-known-face-embedding'
    )

    # submit the request
    response = requests.post(
        MATCH_FACE_EMBEDDING_API_URL, files=payload
    ).json()

    # # ensure the request was successful
    if response["success"]:
        print(f"face_count : {response['face_count']}")

        matches_result = response['matches_result']

        # show detected faces
        i = 1
        for result in matches_result:
            is_matched = result['is_matched']
            print(f"is_matched : {is_matched}")

            probability = result['probability']
            print(f"probability : {probability}")

        #     # convert list type to numpy
        #     np_face_array = asarray(face)
            
        #     # plot
        #     plt.subplot(2, 2, i)
        #     plt.axis('off')
        #     plt.imshow(np_face_array)

        #     # plt.imshow(np_face_array, interpolation='nearest')
        #     i += 1
        # plt.show()
    else:
        print("Request failed")


def test_api_highlight_recognized_faces(image_path, recognized_faces=[]):
    from matplotlib import pyplot as plt

    # load the input image and construct the payload for the request
    image = open(image_path, "rb").read()

    FACE_HIGHTLIGHT_RECOGNIZED_API_URL = urljoin(BASE_API_URL, '/hightlight-recognized-faces')

    if recognized_faces == []:
        recognized_faces = [
            {
                "name": "Nivratti",
                "probability": 0.95,
                "box": (50, 50, 60, 50)
            }
        ]

    data_json = {
        "recognized_faces": recognized_faces
    }

    files = {
        "image": image,
        'json': ("demo.json", json.dumps(data_json), 'application/json'),
    }

    # submit the request
    response = requests.post(
        FACE_HIGHTLIGHT_RECOGNIZED_API_URL, files=files
    ).json()

    # # ensure the request was successful
    if response["success"]:
        encoded_img = response["encoded_img"]
        np_image_array = helpers.base64_to_pil(encoded_img)
        
        # show
        plt.imshow(np_image_array, interpolation='nearest')
        plt.show()
    else:
        print("Request failed")


if __name__ == "__main__":
    from numpy import asarray, loadtxt
    from matplotlib import pyplot as plt

    from timeit import default_timer as timer
    from datetime import timedelta

    start = timer()

    IMAGE_PATH = "media/images/own_grady.jpg"
    
    # #### 1 ###############
    response = test_api_get_face_count(IMAGE_PATH)
    print(response)

    # #### 2 ###############
    # test_api_highlight_faces(IMAGE_PATH)

    # ### 3 ###############
    detected_faces, extracted_faces = test_api_extract_faces_and_embeddings(IMAGE_PATH)
    # # show detected faces
    # i = 1
    # for face in extracted_faces:
    #     # convert list type to numpy
    #     np_face_array = asarray(face)
        
    #     # plot
    #     plt.subplot(2, 2, i)
    #     plt.axis('off')
    #     plt.imshow(np_face_array)

    #     # plt.imshow(np_face_array, interpolation='nearest')
    #     i += 1
    # plt.show()

    # ### 4 ###############
    # file_single_face_embedding = os.path.join(
    #     settings.MEDIA_ROOT, 'face_embedding/single_face_embedding.txt'
    # )
    # np_array_known_embedding = loadtxt(file_single_face_embedding).view(float)
    # print(np_array_known_embedding.shape)
    # print(np_array_known_embedding.dtype) # float64
    # test_api_match_known_face_embedding(np_array_known_embedding, IMAGE_PATH)

    # #### 5 ###############
    # known_embedding = loadtxt('media/face_embedding/single_face_embedding.txt').view(float)
    # response = test_api_compare_face_embedding(known_embedding, known_embedding)

    # #### 6 ###############
    # recognized_faces = []
    # for detected_face in detected_faces:
    #     recognized_faces.append({
    #         "name": "Nivratti",
    #         "probability": response['probability'],
    #         "box": detected_face
    #     })
    # test_api_highlight_recognized_faces(IMAGE_PATH, recognized_faces)

    end = timer()
    print(timedelta(seconds=end-start))
