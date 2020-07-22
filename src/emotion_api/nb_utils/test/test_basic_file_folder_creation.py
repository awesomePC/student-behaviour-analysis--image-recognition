import unittest

import os
import numpy as np
from PIL import Image


# importing-modules-from-parent-folder
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from basic_file_folder_creation import *

class TestBasicFileFolderCreation(unittest.TestCase):

    def test_add_today_date_in_filename(self):
        filename = "n.txt"
        result = add_today_date_in_filename(filename)
        self.assertNotEqual(filename, result, "Date must be added in filename. It must not return same filename.")

    def test_generate_folder(self):
        from tempfile import gettempdir
        base_folder = gettempdir()
        from uuid import uuid4
        folder_name = str(uuid4())
        folder_name_with_path = os.path.join(base_folder, folder_name)
        result = generate_folder(folder_name_with_path)
        self.assertTrue(result, "Folder name not generated.")

    def test_generate_today_date_log_folder(self):
        from tempfile import gettempdir
        base_folder = gettempdir()
        from uuid import uuid4
        folder_name = str(uuid4())
        folder_name_with_path = os.path.join(base_folder, folder_name)

        result = generate_today_date_log_folder(folder_name_with_path)
        self.assertTrue(result, "Logger folder must be generated.")
    
if __name__ == '__main__':
    unittest.main()



def generate_folder(folder_name_with_path):
    """
    * chech is folder exists 
    * if exists or created  return folder name
    * if error occurs return false
    """
    if not os.path.exists(folder_name_with_path):
        try:
            os.makedirs(folder_name_with_path)
        except Exception as e:
            print(e)
            return False
    return folder_name_with_path

def generate_today_date_log_folder(root_log_folder_withpath, exit_ok=True):
    """
    create today date log folder
    
    Keyword Arguments:
        root_log_folder {str} -- [description] (default: {"logs"})
    
    Returns:
        [type] -- [description]
    """  
    now = dt.now()
    current_month_year = now.strftime("%B-%Y")

    today_date = now.strftime("%Y-%m-%d")
    
    # list flating * before list required -- list must not be empty
    today_log_folder = os.path.join(
        root_log_folder_withpath,
        *[current_month_year, today_date]
    )
    # make recursive dir
    os.makedirs(today_log_folder, exist_ok=True)
    return today_log_folder


def check_create_file_with_all_permission(file_name_with_path):
    """
    * check is file exists 
    * If not create file with read write permissions
    """
    if not os.path.exists(file_name_with_path):
        # The default umask is 0o22 which turns off write permission of group and others
        os.umask(0)
        with open(os.open(file_name_with_path, os.O_CREAT | os.O_APPEND, 0o777), 'w') as fh:
            pass
            # print(f"file {file_name_with_path} created with all permissions")
        return True
    else:
        return False

def generate_filename(extension=".txt", base_folder=None):
    """
    Generate unique filename

    Args:
        extension (str, optional): Extension for filename. Defaults to "txt".
        base_folder (str, optional): Base folder path. Defaults to None.
    """
    from text_processing import generate_unique_str
    unique_str = generate_unique_str()

    if not extension.startswith('.'):
        extension = "." + extension

    filename = unique_str + extension

    if base_folder:
        return os.path.join(base_folder, filename)
    else:
        return filename
