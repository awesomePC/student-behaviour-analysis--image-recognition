# import the necessary packages
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json
import sys
 
def pil_to_base64(pil_image, format="JPEG"):
    """
    Convert PIL image to base64
    
    Args:
        pil_image (pillow): Pillow image
        format (str, optional): Image format. Defaults to "JPEG".
    
    Returns:
        str: Image in string format
    """
    buffered = BytesIO()
    pil_image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def base64_to_pil(img_str, dtype="float32"):
    """
    Base64 to PIL Image
    
    Args:
        img_str (str): Image string
        dtype (str, optional): Datatype. Defaults to "float32".
    
    Returns:
        pil_image: PIL image
    """
    img_decoded_str = base64.b64decode(img_str)
    buf = BytesIO(img_decoded_str)

    pil_image = Image.open(buf)

    # return the decoded image
    return pil_image

def np_to_base64(a):
    """
    base64 encode the input NumPy array
    
    Args:
        a (array): numpy array
    
    Returns:
        str: Encoded string
    """
    return base64.b64encode(a).decode("utf-8")
 
def base64_to_np(img_str, dtype=np.uint8):
    """
    Image string to Numpy array
    
    Args:
        img_str (str): Image string
        dtype (numpy, optional): Numpy Datatype. Defaults to np.uint8.
    """
    # if this is Python 3, we need the extra step of encoding the
    # serialized NumPy string as a byte object
    if sys.version_info.major == 3:
        img_bytes = bytes(img_str, encoding="utf-8")
 
    # convert the string to a NumPy array using the supplied data
    # type and target shape
    np_img = np.frombuffer(base64.decodestring(img_bytes), dtype=dtype)

    # return the decoded image as numpy array
    return np_img



# class JsonNumpyEncoder(json.JSONEncoder):
#     """
#     If obj is isinstance of ndarray then it convert to list to support json
#     """
#     def default(self, obj):
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return json.JSONEncoder.default(self, obj)

# more advanced encoder - with float and integer
# implement it later as separate package
# use - json.dumps(data, cls=MyEncoder)
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()

        elif isinstance(obj, Decimal):
            return float(obj)
        
        elif isinstance(obj, complex):
            return {
                "real": obj.real,
                "imag": obj.imag,
                "__class__": "complex"
            }
        else:
            return super(MyEncoder, self).default(obj)


# print json.dumps(2 + 1j, cls=ComplexEncoder)
# OUTPUT
# {"real": 2.0, "imag": 1.0, "__class__": "complex"}