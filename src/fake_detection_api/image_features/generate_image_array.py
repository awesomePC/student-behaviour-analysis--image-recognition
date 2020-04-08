
import numpy as np
from PIL import Image

image_array = np.asarray(Image.open('1.jpg'))

print(image_array.shape)