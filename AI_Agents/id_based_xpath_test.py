from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from driver_setup import setup_driver
from idBased import get_ai_suggestion

def test_id_based_xpath():
    driver = setup_driver()
    driver.get("https://the-internet.herokuapp.com/login")

    failing_locator = "input#wrong-id"  # Incorrect locator
    correct_locator = "input#username"  # Correct locator

    try:
        driver.find_element(By.CSS_SELECTOR, failing_locator).send_keys("test")
        print("Test Passed with initial locator!")
    except NoSuchElementException:
        html_source = driver.page_source
        suggested_locator = get_ai_suggestion(failing_locator, html_source)
        print(f"AI suggested: {suggested_locator}")
        try:
            driver.find_element(By.CSS_SELECTOR, suggested_locator).send_keys("test")
            print("Test Passed with AI-suggested locator!")
        except Exception as e:
            print(f"Test Failed after AI suggestion: {e}")
    driver.quit()

if __name__ == "__main__":
    test_id_based_xpath()
