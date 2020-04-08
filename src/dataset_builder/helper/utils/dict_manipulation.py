import logging
import dpath

import sys, traceback

from functools import reduce
import operator

logger = logging.getLogger(__name__)
# print(__name__)

def get_dict_nested_key_value(dictionary, path, default=None, log=False):
    """
     accessing and searching dictionaries via /slashed/paths ala xpath
    
    Arguments:
        dictionary {dict} -- Input dictionary nested elements
        path {string} --  slashed dict path

    Usage:
        >> x = {
                "a": {
                    "b": {
                    "3": 2,
                    "43": 30,
                    "c": [],
                    "d": ['red', 'buggy', 'bumpers'],
                    }
                }
            }

        >> get_dict_nested_key_value(x, "/a/b/d/0")
           red
    """
    nested_value_with_root = dpath.util.search(dictionary, path)
    if nested_value_with_root:
        nested_value = dpath.util.get(dictionary, path)
        if log:
            logger.debug(f" Fetched value : {nested_value} from dict by path {path}")
        return nested_value
    else:
        logger.error(f'Cannot fetch value from dict by path {path}')
        return default

def check_dict_keys_not_empty(d):
    """
    * check if dictionary key has empty value by recursive method
    @ parameters -
        * d - Dictionary 
    @ Output:
        * True/ False value indicating whether all dict keys are not null
    """
    is_keys_not_empty = False
    
    for k, v in d.items():
        if isinstance(v, dict):
          check_dict_keys_not_empty(v)
        else:
          if v:
              is_keys_not_empty = True
              break
    return is_keys_not_empty


def sum_values_in_dict(list_of_dicts, key_name):
    """
    # sum values in dictionary
    # ex.
    example_list = [
        {'points': 400, 'gold': 80},
        {'points': 100, 'gold': 10},
        {'points': 100, 'gold': 10},
        {'points': 100, 'gold': 10}
    ]
    then 
        sum(item['gold'] for item in myLIst)
    returns:
        110
    """
    sum = None

    if list_of_dicts:
        if isinstance(list_of_dicts, (list,)):
            sum = 0
            for val_dict in list_of_dicts:
                if key_name in val_dict:
                    sum += val_dict[key_name]
                else:
                    print(f"list of dictionary has no key with name {key_name}")
                    sum = None
                    break
        else:
            print(f"list of dictionary is not instance of list type its type is {type(list_of_dicts)}")
    else:
        print("list of dictionary cannot be empty")
    return sum

def get_multi_occurrence_key_value(list_of_dicts, key_name, log=False):
    """
    # Get value of key that occurs multiple times in dictionaries of list
    # ex.
    example_list = [
        {'points': 400, 'gold': 80},
        {'points': 100, 'gold': 10},
        {'points': 100, 'gold': 10},
        {'points': 100, 'gold': 10}
    ]
    then 
        get_multi_occurrence_key_value(example_list, points)
    returns:
        [400, 100, 100, 100]
    """
    result_list = []

    if list_of_dicts:
        if isinstance(list_of_dicts, (list,)):
            for val_dict in list_of_dicts:
                #print(list_of_dicts)
                if key_name in val_dict:
                    result_list.append(val_dict[key_name])
                else:
                    print(f"list of dictionary has no key with name '{key_name}'")
                    break
        else:
            print(f"list of dictionary is not instance of list type its type is {type(list_of_dicts)}")
    else:
        print("list of dictionary cannot be empty")
    if log:
        logger.debug(
            f"Result list after getting multi occurred key value from list of dicts {result_list}"
        )
    return result_list


def remap_dict_key_val_convert_2_list(data_dict, remaped_key_name, remaped_value_name):
    """
    # sum values in dictionary
    # ex.
    dict = {
        'Adelaide, SA, Australia': 13318, 
        'Albury, NSW, Australia': 523, 
    }

    if 
    remaped_key_name = "country"
    country = "count"
    
    remap_dict_key_val_convert_2_list(dict, remaped_key_name, remaped_value_name)

    output: 
        example_list = [{
            "country": 'Adelaide, SA, Australia',
            "count": 13318
        },
        {
            "country": 'Albury, NSW, Australia',
            "count": 523
        }]
    """
    data_list = []

    if data_dict:
        logger.debug(f"Dictionary {data_dict} ")
        try:
            for key, value in data_dict.items():
                single_record_dict = {
                    remaped_key_name: key,
                    remaped_value_name: value
                }
                data_list.append(single_record_dict)
            
            logger.debug(f"Dictionary key values pair is converted to {data_list} ")
        except Exception as e:
            logger.warning(f"Error {e}")
    else:
        logger.debug(f"list of dictionary cannot be empty")
    return data_list

def delete_nested_dict_key(dictionary, key_list):
    """
    Delete nested key
    
    Arguments:
        dictionary {[type]} -- [description]
        key_list {[type]} -- [description]
    """
    *path, key = key_list
    del reduce(operator.getitem, path, dictionary)[key]
