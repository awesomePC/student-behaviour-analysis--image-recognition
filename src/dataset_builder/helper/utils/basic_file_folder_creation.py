import os
import json

from datetime import datetime as dt

# from config.settings import root_path

def add_today_date_in_filename(file_name, format="%Y-%m-%d"):
    """
    * Add date inside filename
    * file_util_logger.txt  to file_util_logger_04-12-2018.txt
    """
    try:
        today_date = dt.now().strftime(format)
        
        filename_no_ext, file_extension = os.path.splitext(file_name)
        filename_no_ext = f"{filename_no_ext}-{today_date}"
        # print("today_date ", today_date)
        
        name_with_date = filename_no_ext + file_extension
        # print("modified filename :", name_with_date)
        return name_with_date
    
    except Exception as e:
        print("Error :", e)
        return file_name

def check_or_create_folder(folder_name_with_path):
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



def create_or_get_today_date_log_folder(root_log_folder_withpath):
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
