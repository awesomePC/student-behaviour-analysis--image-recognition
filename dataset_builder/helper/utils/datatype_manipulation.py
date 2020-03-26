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
