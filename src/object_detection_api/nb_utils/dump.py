
import os
import logging
import json

from datetime import datetime as dt

# dump table json
from bson import Binary, Code
from bson import json_util

import pickle

from config.settings import root_folder_raw_dump, root_folder_script_status

from utils.basic_file_folder_creation import check_create_file_with_all_permission

logger = logging.getLogger(__name__)
# print(__name__)

def dump_raw_table(db, raw_table_name, filename="raw_file_name"):
    """
    Dump raw table data in json file
    
    Arguments:
        db {mongo} -- Database connectivity object
        raw_table_name {str} -- Raw table name mapping
    
    Keyword Arguments:
        filename {str} -- Name of raw file (default: {"raw_file_name"})
    """
    now = dt.now()
    current_month_year = now.strftime("%B-%Y")

    today_date = now.strftime("%Y-%m-%d")
    today_raw_dump_folder_with_path = os.path.join(
        root_folder_raw_dump,
        *[current_month_year, today_date]
    )

    os.makedirs(today_raw_dump_folder_with_path, exist_ok=True)

    # write data
    filename_ext = f"{filename}.json"
    filename_with_path = os.path.join(today_raw_dump_folder_with_path, filename_ext)

    is_created = check_create_file_with_all_permission(filename_with_path)

    # finally generate final.json
    collection_data = db[raw_table_name].find()
    with open(filename_with_path, 'w') as jsonfile:
        jsonfile.write(json_util.dumps(collection_data))


def write_page_status(pickle_script_status_file_name, region_status):
    """
    Write today script status for each channel

    Arguments:
        pickle_script_status_file_name {str} -- File name for pickle
        region_status {dict} -- region status successfull data fetching or error info
    
    Returns:
        Boolean -- Return true on success
    """

    now = dt.now()
    current_month_year = now.strftime("%B-%Y")

    today_date = now.strftime("%Y-%m-%d")
    today_script_status_folder_with_path = os.path.join(
        root_folder_script_status,
        *[current_month_year, today_date]
    )

    os.makedirs(today_script_status_folder_with_path, exist_ok=True)
    
    filename_with_path = os.path.join(
        today_script_status_folder_with_path,
        pickle_script_status_file_name
    )

    regions_status_list = []

    if os.path.exists(filename_with_path):
        # append data to existing
        with open(filename_with_path, 'rb') as f:
            regions_status_list = pickle.load(f)

        regions_status_list.append(region_status)
        # write it back
        with open(filename_with_path, 'wb') as f:
            pickle.dump(regions_status_list, f)
    else:
        # create new pickle
        regions_status_list.append(region_status)
        # write it back
        with open(filename_with_path, 'wb') as f:
            pickle.dump(regions_status_list, f)
    return True
        
