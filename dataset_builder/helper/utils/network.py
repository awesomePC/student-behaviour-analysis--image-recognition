
import logging
import socket

logger = logging.getLogger(__name__)
# print(__name__)

def is_internet_connected(hostname="www.google.com"):
    """
    * Check internet connectivity
    -----------------------------
    * see if we can resolve the host name -- tells us if there is
    * a DNS listening
    * connect to the host -- tells us if the host is actually reachable
    """
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 2)
        return True
    except Exception as e:
        logger.error(f"Network .. Error ... Server not reachable ... {e}")
        pass
    return False
