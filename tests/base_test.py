import pytest
from selenium import webdriver
from config.config import SELENIUM_DRIVER_PATH, BASE_URL

@pytest.fixture(scope="class")
def setup(request):
    driver = webdriver.Chrome(SELENIUM_DRIVER_PATH)
    driver.get(BASE_URL)
    driver.maximize_window()

    request.cls.driver = driver
    yield
    driver.quit()
