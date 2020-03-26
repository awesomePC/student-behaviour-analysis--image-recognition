
from functools import reduce  # forward compatibility for Python 3
import operator
from itertools import groupby
from operator import add, itemgetter

def list_2_str(input_list=[], separator=",", log=False):
    """
    * convert list to string
    ------------------------
    @ parameters: 
        * input list contaning strings
        * separator used to convert list to string
    -----------------------------------------------
    @ outputs:
        * string (Joined if list not empty or "")
    """
    if input_list:
        result_str = f"{separator}".join(map(str, input_list))
        if log:
            logger.debug(
                f'list {input_list} converted to string "{result_str}"'
            )
        return result_str
    else:
        logger.error(f'Empty list detected while converting to string ...')
        return ""


def merge_records_by(key, combine):
    """Returns a function that merges two records rec_a and rec_b.
       The records are assumed to have the same value for rec_a[key]
       and rec_b[key].  For all other keys, the values are combined
       using the specified binary operator.
    """
    return lambda rec_a, rec_b: {
        k: rec_a[k] if k == key else combine(rec_a[k], rec_b[k])
        for k in rec_a
    }

def merge_list_of_records_by(key, combine):
    """
    Returns a function that merges a list of records, grouped by
    the specified key, with values combined using the specified
    binary operator.
    
    usage:
        a=[{'time': '25 APR', 'total': 10, 'high': 10}, 
           {'time': '26 APR', 'total': 5, 'high': 5}]
        
        b=[{'time': '24 APR', 'total': 10, 'high': 10}, 
           {'time': '26 APR', 'total': 15, 'high': 5}]

        merger = merge_list_of_records_by('time', add)
        
        print(merger(a + b))
        will print ..
        
        [
            {'time': '24 APR', 'total': 10, 'high': 10},
            {'time': '25 APR', 'total': 10, 'high': 10}, 
            {'time': '26 APR', 'total': 20, 'high': 10}
        ]
    """
    keyprop = itemgetter(key)
    return lambda lst: [
        reduce(merge_records_by(key, combine), records)
        for _, records in groupby(sorted(lst, key=keyprop), keyprop)
    ]
