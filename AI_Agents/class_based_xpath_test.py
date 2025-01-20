from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from driver_setup import setup_driver
from classBased import get_ai_suggestion

def test_class_based_xpath():
    driver = setup_driver()
    driver.get("https://the-internet.herokuapp.com/add_remove_elements/")

    failing_locator = ".added-human"  # Incorrect locator
    correct_locator = ".added-manually"  # Correct locator

    try:
        driver.find_element(By.CSS_SELECTOR, failing_locator).click()
        print("Test Passed with initial locator!")
    except NoSuchElementException:
        html_source = driver.page_source
        suggested_locator = get_ai_suggestion(failing_locator, html_source)
        print(f"AI suggested: {suggested_locator}")
        try:
            driver.find_element(By.CSS_SELECTOR, suggested_locator).click()
            print("Test Passed with AI-suggested locator!")
        except Exception as e:
            print(f"Test Failed after AI suggestion: {e}")
    driver.quit()

if __name__ == "__main__":
    test_class_based_xpath()
