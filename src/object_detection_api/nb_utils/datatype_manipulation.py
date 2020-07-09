import sys, traceback

def is_float(value):
    """
    Check is value convertable to float
    
    Arguments:
        value {string/int} -- Either string or integer
    
    Returns:
        Boolean -- Either True or False
    """

    if value:
        if isinstance(value, str) or isinstance(value, int):
            try:
                float(value)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return False


def truncate_float(value, digits_after_point=2):
    """
    Truncate long float numbers
    >>> truncate_float(1.1477784, 2)
       1.14
    """
    pow_10 = 10 ** digits_after_point
    return (float(int(value * pow_10))) / pow_10
