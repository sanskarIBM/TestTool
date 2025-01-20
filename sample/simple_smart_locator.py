from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


class SimpleSmartLocator:
    def __init__(self):
        self.element_memory = {}

    def learn_element(self, driver, locator, friendly_name):
        """Learn an element's characteristics"""
        element = driver.find_element(*locator)
        self.element_memory[friendly_name] = {
            'original_locator': locator,
            'tag_name': element.tag_name,
            'text': element.text,
            'location': element.location,
            'type': element.get_attribute('type'),
            'name': element.get_attribute('name'),
            'class_name': element.get_attribute('class'),
            'parent_text': element.find_element(By.XPATH, "..").text
        }
        print(f"Learned {friendly_name} characteristics: {self.element_memory[friendly_name]}")
        return element

    def find_element(self, driver, friendly_name):
        """Find element using multiple strategies"""
        original = self.element_memory.get(friendly_name)
        if not original:
            raise Exception(f"Element {friendly_name} not learned yet")

        strategies = [
            # Try original locator
            lambda: driver.find_element(*original['original_locator']),

            # Try by name attribute
            lambda: driver.find_element(By.NAME, original['name']) if original['name'] else None,

            # Try by type and tag combination
            lambda: driver.find_element(
                By.XPATH,
                f"//{original['tag_name']}[@type='{original['type']}']"
            ) if original['type'] else None,

            # Try by exact button text
            lambda: driver.find_element(
                By.XPATH,
                f"//button[text()='{original['text']}']"
            ) if original['tag_name'] == 'button' else None,

            # Try by partial button text
            lambda: driver.find_element(
                By.XPATH,
                f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{original['text'].lower()}')]"
            ) if original['tag_name'] == 'button' else None,

            # Try by type attribute for buttons
            lambda: driver.find_element(
                By.XPATH,
                f"//button[@type='submit']"
            ) if original['tag_name'] == 'button' and original['type'] == 'submit' else None,

            # Try by position in form
            lambda: driver.find_element(
                By.XPATH,
                f"//form//button"
            ) if original['tag_name'] == 'button' else None,

            # Try by any button in a form
            lambda: driver.find_element(
                By.CSS_SELECTOR,
                "form button"
            ) if original['tag_name'] == 'button' else None
        ]

        for i, strategy in enumerate(strategies):
            try:
                element = strategy()
                if element:
                    print(f"Found {friendly_name} using strategy #{i}")
                    return element
            except:
                continue

        raise Exception(f"Could not find element {friendly_name} with any strategy")


def main():
    # Create HTML file
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Login Page</title>
    <style>
        body { 
            font-family: Arial; 
            display: flex;
            justify-content: center;
            padding-top: 50px;
        }
        .login-form {
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .form-group {
            margin: 10px 0;
        }
        input {
            padding: 8px;
            width: 200px;
            margin-top: 5px;
        }
        button {
            padding: 8px 15px;
            background: #0077b5;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <form class="login-form">
        <div class="form-group">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username">
        </div>
        <div class="form-group">
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password">
        </div>
        <div class="form-group">
            <button id="login" type="submit">Login</button>
        </div>
    </form>

    <script>
        // Simulate UI changes after 5 seconds
        setTimeout(() => {
            document.getElementById('username').id = 'user_email';
            document.getElementById('password').id = 'user_pwd';
            document.getElementById('login').id = 'signin';
            document.querySelector('button').textContent = 'Sign In';
        }, 5000);
    </script>
</body>
</html>'''

    # Save HTML to a temporary file
    with open('test_login.html', 'w') as f:
        f.write(html_content)

    # Setup WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # Initialize our smart locator
        smart_locator = SimpleSmartLocator()

        # Load the page
        file_path = os.path.abspath('test_login.html')
        driver.get(f"file:///{file_path}")

        print("\nLearning original elements...")
        username = smart_locator.learn_element(driver, (By.ID, "username"), "username_field")
        password = smart_locator.learn_element(driver, (By.ID, "password"), "password_field")
        login = smart_locator.learn_element(driver, (By.ID, "login"), "login_button")

        print("\nTesting original elements...")
        username.send_keys("test@example.com")
        password.send_keys("password123")
        print("Filled in original form fields")

        print("\nWaiting for UI changes (5 seconds)...")
        time.sleep(10)

        print("\nTesting elements after UI changes...")
        username = smart_locator.find_element(driver, "username_field")
        password = smart_locator.find_element(driver, "password_field")
        login = smart_locator.find_element(driver, "login_button")

        # Test the elements again
        username.clear()
        username.send_keys("new@example.com")
        password.clear()
        password.send_keys("newpassword123")
        login.click()

        print("\nSuccess! All elements found and interacted with before and after UI changes!")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

    finally:
        time.sleep(2)  # Wait to see the results
        driver.quit()
        os.remove('test_login.html')  # Clean up


if __name__ == "__main__":
    main()