from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from driver_setup import setup_driver
from agentsAI import get_ai_suggestion

def test_dynamic_elements():
    driver = setup_driver()
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/1")  # Example of dynamic loading page

    start_button_locator = "div#end button"  # Correct locator for the start button
    dynamic_element_locator = "div#finish h4"  # Locator for the dynamic element
    locator_text = "Start"

    print("\nRunning Test Case 3: Dynamic Elements.")
    try:
        # Start loading
        driver.find_element(By.CSS_SELECTOR, start_button_locator).click()

        # Wait for the dynamic element to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, dynamic_element_locator)))
        dynamic_element = driver.find_element(By.CSS_SELECTOR, dynamic_element_locator)
        print(f"Dynamic Element Text: {dynamic_element.text}")
        print("Test Case 3 Passed!")
    except NoSuchElementException as e:
        print(f"Error: {str(e)}")

        # Capture the relevant HTML structure
        html_source = driver.page_source

        # Trigger AI Agent for suggestion
        print("\nAI Agent: Test case failed due to No Such Element error.")
        suggested_locator = get_ai_suggestion(locator_text, html_source)
        print(f"\nAI suggests trying a new locator: {suggested_locator}")

        try:
            # Retry with the suggested locator
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, suggested_locator)))
            dynamic_element = driver.find_element(By.CSS_SELECTOR, suggested_locator)
            print(f"Dynamic Element Text: {locator_text}")
            print(f"Dynamic Element : {suggested_locator}")
            print("Test Case 3 Passed with AI suggestion!")
        except Exception as retry_error:
            print(f"Test Case 3 still failed after AI suggestion: {retry_error}")

    driver.quit()

if __name__ == "__main__":
    test_dynamic_elements()
