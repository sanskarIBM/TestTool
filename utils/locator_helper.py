from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def find_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except NoSuchElementException:
        raise NoSuchElementException(f"Element not found using {by}: {value}")
