from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def find_element_safe(driver, locator):
    try:
        element = driver.find_element(By.XPATH, locator)
        return element
    except NoSuchElementException as e:
        raise NoSuchElementException(f"Element not found: {locator}") from e
