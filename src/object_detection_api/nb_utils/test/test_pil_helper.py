import unittest

import os
import numpy as np
from PIL import Image


# importing-modules-from-parent-folder
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from pil_helper import save_array

class TestPilHelper(unittest.TestCase):

    def test_save_array(self):
        img = Image.new('RGB', (60, 30), color = 'red')
        img_array = np.array(img)
        
        filename = save_array(img_array)
        self.assertTrue(filename, "File must be saved. It must return filename.")

if __name__ == '__main__':
    unittest.main()

