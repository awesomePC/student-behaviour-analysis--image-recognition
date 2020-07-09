import logging
import os
import json
from pprint import pprint
from datetime import datetime as dt

from config.settings import root_folder_api_response
from utils.basic_file_folder_creation import add_today_date_in_filename
from utils.basic_file_folder_creation import check_create_file_with_all_permission

logger = logging.getLogger(__name__)
# print(__name__)

def write_api_response(json_data={}, filename_prefix="N"):
    """
    Write json response to file
    
    Keyword Arguments:
        json_data {dict} -- Json data (default: {})
        filename_prefix {str} -- Name for json file (default: {"N"})
    """
    if write_api_response:
        if json_data:
            now = dt.now()
            current_month_year = now.strftime("%B-%Y")

            today_date = now.strftime("%Y-%m-%d")
            
            today_api_folder_with_path = os.path.join(
                root_folder_api_response,
                *[current_month_year, today_date]
            )
            
            # create folder if not exists
            os.makedirs(today_api_folder_with_path, exist_ok=True)

            # write data
            respose_filename = f"{filename_prefix}.json"
            filename_with_time = add_today_date_in_filename(
                respose_filename, format="%Y-%m-%d-time-%H-%M-%S-%f"
            )
            filename_with_path = os.path.join(
                today_api_folder_with_path, filename_with_time
            )

            is_created = check_create_file_with_all_permission(filename_with_path)

            with open(filename_with_path, 'w') as outfile:
                json.dump(json_data, outfile, indent=4)
                logger.debug(
                    f"json response written to file {filename_with_path}"
                )

        else:
            logger.warning(
                f"json response is empty so skipping writing to file"
            )
    else:
        logger.warning(
            f"write_api_response is false so skipping writing to file"
        )

# def print_data(message, hold_program=True, hold_message="Press any key to continue", use_pprint=True, print_json=False):
#     """
#     * IT will print data if debug is true
#     """

#     print("\n\n")
#     if use_pprint and not print_json:
#         pprint(message)
#     if print_json:
#         print(json.dumps(message, indent=4, sort_keys=True))
#     else:
#         print(message)

#     if hold_program:
#         input(hold_message)
