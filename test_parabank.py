from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from utils.driver_factory import DriverFactory

# Configure logging
logging.basicConfig(level=logging.INFO)


def test_parabank_login():
    driver = DriverFactory.get_driver()
    try:
        driver.get("https://www.parabank.com")

        # Wait for the login button to be clickable
        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Log In']"))
            )
            login_button.click()

        except Exception as e:
            logging.error(f"Error encountered: {e}")
            failed_locator = "//input[@value='Log In']"

            # AI agent suggestion for a better locator
            ai_fix = DriverFactory.suggest_fix(str(e), failed_locator)
            if ai_fix:
                logging.info(f"AI suggests: {ai_fix}")
            else:
                logging.error("AI could not suggest a fix.")

    finally:
        # Quit the driver after test
        DriverFactory.quit_driver(driver)
