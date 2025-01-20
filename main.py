

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from webdriver_manager.chrome import ChromeDriverManager
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
# Function to suggest AI-based fixes using Groq's LLM
def get_ai_suggestion(locator):
    prompt = (
        f"Error: NoSuchElementException. "
        f"Current locator used: {locator}. "
        f"Please suggest only the most accurate and optimal locator to resolve this issue. "
        f"Ensure the locator is in the exact format: tagname[attribute='value'], no additional text or explanation."
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        # Extracting the text from the Groq response
        response = chat_completion.choices[0].message.content
        return response.strip()
    except Exception as e:
        return f"Failed to get a suggestion from Groq: {str(e)}"


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    driver.get("https://parabank.parasoft.com/parabank/index.htm")
    return driver


def login(driver, username_locator):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, username_locator)))

        username_element = driver.find_element(By.CSS_SELECTOR, username_locator)
        password_element = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//input[@value='Log In']")

        username_element.send_keys("john")
        password_element.send_keys("demo")
        login_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("overview"))
        print("Login Successful!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def run_test_case():
    driver = setup_driver()

    # Initial valid locator (Test Case 1 - Pass)
    username_locator = "input[name='username']"
    print("\nRunning Test Case 1: Using valid locator.")
    if login(driver, username_locator):
        print("Test Case 1 Passed!")
    else:
        print("Test Case 1 Failed!")
    driver.quit()


    driver = setup_driver()
    # Change the locator (Test Case 2 - Fail)
    username_locator = "input[name='username1']"
    print("\nRunning Test Case 2: Using invalid locator (Should Fail).")
    if login(driver, username_locator):
        print("Test Case 2 Passed!")
    else:
        print("Test Case 2 Failed!")

        # Trigger AI Agent for suggestion
        print("\nAI Agent: Test case failed due to No Such Element error.")
        suggested_locator = get_ai_suggestion(username_locator)

        print(f"\nAI suggests trying a new locator: {suggested_locator}")
        print("\nRetrying the test case with the new locator...")

        if login(driver, suggested_locator):
            print("Test Case passed with the suggested locator!")
        else:
            print("Test Case still failed even after AI suggestion.")

    driver.quit()


if __name__ == "__main__":
    run_test_case()
