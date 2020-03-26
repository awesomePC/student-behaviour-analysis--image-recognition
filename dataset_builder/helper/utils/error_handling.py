import sys, traceback

def trace_error():
    """
    Trace current error info
    
    Returns:
        str -- string representation of error
    """
    err_type, value, tb = sys.exc_info()
    error = ''.join(
        traceback.format_exception(
            err_type, value, tb
        )
    )
    return error
