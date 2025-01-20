import pytest
from selenium import webdriver

@pytest.fixture
def setup():
    # Example: Set up a Selenium WebDriver instance
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver  # Provide the WebDriver to the test
    driver.quit()  # Clean up after the test
