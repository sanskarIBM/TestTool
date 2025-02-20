from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from self_healing import find_element_with_recovery

driver = webdriver.Chrome()

driver.get(r"C:\Users\SanskarZanwar\Downloads\SelfHeal\TestTool\TwoPointO\index.html")  # Update this with the correct file path

# Function to fill a text field
def fill_field(field_name, value):
    field = find_element_with_recovery(driver, field_name)
    if field:
        field.send_keys(value)
        field.send_keys(Keys.TAB)
        time.sleep(1)

try:
    fill_field("firstName", "John")
    fill_field("middleName", "Michael")
    fill_field("lastName", "Doe")

    submit_button = find_element_with_recovery(driver, "submitBtn")
    if submit_button:
        submit_button.click()

    print("Test completed successfully!")

except Exception as e:
    print(f"Test failed: {e}")

time.sleep(5)
driver.quit()
