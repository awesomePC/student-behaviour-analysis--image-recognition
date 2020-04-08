
import logging

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime as dt

from config.settings import selenium_executable_path
from config.settings import root_folder_screenshot, is_capture_selenium_screenshot


logger = logging.getLogger(__name__)
# print(__name__)


def get_selenium_driver(headless=False, start_minimal=True):
    """
    * Initialize selenium driver
    """
    options = Options()
    if headless:
        options.add_argument("--headless") # Runs Chrome in headless mode. # may detected by facebook
    
    if start_minimal:
        options.add_argument('--no-sandbox') # Bypass OS security model
        options.add_argument('--disable-gpu')  # applicable to windows os only
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")

    try:
        driver = webdriver.Chrome(
            chrome_options=options,
            executable_path=selenium_executable_path,
            # service_args=['--verbose', '--log-path=chromedriver.log']
        )
        return driver
    except Exception as e:
        message = f'Error while getting selenium webdriver-- {e}'
        logger.error(message)
        print(message)


def selenium_get_url_data(driver, url, sleep_time=9):
    """
    * Fetch url by selenium driver
    """
    try:
        driver.get(url)
        
        if is_capture_selenium_screenshot:
            file_name = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            driver.save_screenshot(f"{root_folder_screenshot}/{file_name}.png")

        time.sleep(sleep_time)

        return driver
    except Exception as e:
        logger.error(f'Error while getting url using selenium webdriver-- {e}')
    
        
def wait_find_element(
    driver=None, element_wait_by=By.ID,
    element_to_wait=None, timeout=15, pattern=None
):
    """
    * wait for 15 seconds until presence of parent is located
    ---------------------------------------------------------
    @ inputs:
        * element_wait_by -- Parent element find selector (we are waiting for its visibility)
        * element_to_wait -- Parent element name (we are waiting for its visibility)
        * pattern - pattern_to_find_inner_element
        * timeout -- Max time to wait for element visibility
        * pattern -- pattern to find inner element
    --------------------------------------------------------
    @ output:
        * returns selenium element or false
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((element_wait_by, element_to_wait))
        )
        if pattern:
            inner_element = element.find_element_by_xpath(pattern)  # "//div[contains(text(), 'like')]"
            logger.debug(
                f'Presence of element {element_to_wait} located by selenium'
            )
            logger.debug(
                f'selenium successfully fetched element from pattern {pattern}'
            )
            return inner_element
        else:
            return element

    except Exception as e:
        logger.error(f'Error while waiting for element {element_to_wait} pattern {pattern} -- {e}')       
        
        
def wait_find_elements(
    driver=None, element_wait_by=By.ID, element_to_wait=None,
    timeout=15, find_childs_by=By.CSS_SELECTOR, pattern=None
):
    """
    * wait for 15 seconds until presence of parent is located
    ---------------------------------------------------------
    @ inputs:
        * element_wait_by -- Parent element find selector (we are waiting for its visibility)
        * element_to_wait -- Parent element name (we are waiting for its visibility)
        * pattern - pattern_to_find_inner_element
        * timeout -- Max time to wait for element visibility
    --------------------------------------------------------
    @ output:
        * returns selenium elements list or false
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((element_wait_by, element_to_wait))
        )
        
        # "//div[contains(text(), 'like')]"
        inner_elements = element.find_elements(
            find_childs_by, pattern
        ) 

        logger.debug(
            f'Presence of elements {element_to_wait} located by selenium'
        )
        logger.debug(
            f'selenium successfully fetched elements from pattern {pattern}'
        )
        return inner_elements

    except Exception as e:
        logger.error(f'Error while waiting for element {element_to_wait} pattern {pattern} -- {e}')       


def close_selenium_driver(driver, destroy_cookies=True):
    """
    * close selenium browser 
    * destroys cookies if true
    """
    try:
        if driver:
            if destroy_cookies:
                driver.delete_all_cookies()
            
            driver.close() # closes single session
            # driver.quit() # closes all windows
            return True
    except Exception as e:
        logger.error(f'Error while closing selenium -- {e}')
        return False       
