import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
from difflib import SequenceMatcher
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

class EnhancedSmartLocator:
    def __init__(self):
        self.element_memory = {}
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))

    def _get_element_features(self, element):
        try:
            attrs = element.get_property('attributes')
            attr_dict = {attr['name']: attr['value'] for attr in attrs}
            surrounding_text = element.find_element(By.XPATH, "..").text
            xpath = self._generate_relative_xpath(element)
            css_path = self._generate_css_path(element)
            # Collecting the features of the element based on the following parameters
            return {
                'tag_name': element.tag_name,
                'text': element.text.strip(),
                'attributes': attr_dict,
                'location': element.location,
                'size': element.size,
                'surrounding_text': surrounding_text,
                'xpath': xpath,
                'css_path': css_path,
                'classes': element.get_attribute('class'),
                'id': element.get_attribute('id'),
                'name': element.get_attribute('name'),
                'type': element.get_attribute('type'),
                'value': element.get_attribute('value'),
                'data_testid': element.get_attribute('data-testid')
            }
        except:
            return None

    def _generate_relative_xpath(self, element): # ID based Xpath Generation
        try:
            script = """
            function getXPath(element) {
                if (!element) return '';
                if (element.id) return `//*[@id="${element.id}"]`;

                const sameTagSiblings = Array.from(element.parentNode.children)
                    .filter(e => e.tagName === element.tagName);

                const idx = sameTagSiblings.indexOf(element) + 1;

                return `${getXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
            }
            return getXPath(arguments[0]);
            """
            return element.parent.execute_script(script, element)
        except:
            return None

    def _generate_css_path(self, element):
        try:
            script = """
            function getCssPath(element) {
                if (!element) return '';
                if (element.id) return `#${element.id}`;

                let path = element.tagName.toLowerCase();
                if (element.className) {
                    path += `.${element.className.split(' ').join('.')}`;
                }

                return `${getCssPath(element.parentNode)} > ${path}`;
            }
            return getCssPath(arguments[0]);
            """
            return element.parent.execute_script(script, element)
        except:
            return None

    def _calculate_similarity_score(self, features1, features2):
        score = 0

        def fuzzy_match(a, b):
            return SequenceMatcher(None, a, b).ratio()

        text1 = f"{features1['text']} {features1['surrounding_text']}"
        text2 = f"{features2['text']} {features2['surrounding_text']}"
        text_similarity = fuzzy_match(text1, text2) * 0.3
        score += text_similarity

        common_attrs = set(features1['attributes'].keys()) & set(features2['attributes'].keys())
        attr_similarity = sum(
            fuzzy_match(features1['attributes'][attr], features2['attributes'][attr])
            for attr in common_attrs
        )
        score += (attr_similarity / len(common_attrs)) * 0.3 if common_attrs else 0

        if features1['location'] and features2['location']:
            pos_diff = abs(features1['location']['x'] - features2['location']['x']) + \
                       abs(features1['location']['y'] - features2['location']['y'])
            score += (1 / (1 + pos_diff / 50)) * 0.2

        tag_similarity = 1 if features1['tag_name'] == features2['tag_name'] else 0
        score += tag_similarity * 0.2

        return score

    def learn_element(self, driver, locator, friendly_name):
        element = driver.find_element(*locator)
        features = self._get_element_features(element)
        if features:
            self.element_memory[friendly_name] = {
                'original_locator': locator,
                'features': features
            }
            print(f"Learned {friendly_name} with features: {features}")
        return element

    def find_element(self, driver, friendly_name):
        if friendly_name not in self.element_memory:
            raise Exception(f"Element {friendly_name} not learned yet")

        original = self.element_memory[friendly_name] # the n-1

        try:
            return driver.find_element(*original['original_locator'])
        except:
            print(f"Original locator failed for {friendly_name}, trying ML matching...")

            potential_elements = driver.find_elements(By.XPATH, "//*") # solely working for ID based
            best_match = None
            best_score = 0

            for element in potential_elements:
                try:
                    current_features = self._get_element_features(element)
                    if current_features:
                        similarity_score = self._calculate_similarity_score(
                            original['features'],
                            current_features
                        )

                        if similarity_score > best_score and similarity_score > 0.1:
                            best_score = similarity_score
                            best_match = element
                except:
                    continue

            if best_match:
                print(f"Found {friendly_name} with similarity score: {best_score}")
                return best_match

            raise Exception(f"Could not find {friendly_name} with any strategy")

def get_ai_suggestion(locator, html_source):
    prompt = (
        "You are an advanced AI model tasked with assisting in locating web elements in dynamically changing web pages. "
        "Given the HTML source code and a specific locator description, you will provide suggestions to "
        "adjust the locator to adapt to changes in the DOM. "
        "The locator is described as: {locator}. "
        "Analyze the given HTML source code: {html_source} "
        "and suggest an optimal strategy to locate this element reliably, even after dynamic UI updates. "
        "Provide a concise and practical solution with detailed reasoning."
    ).format(locator=locator, html_source=html_source)

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
        response = chat_completion.choices[0].message.content
        return response.strip()
    except Exception as e:
        return f"Failed to get a suggestion from Groq: {str(e)}"

def main():
    with open('complex_login.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Login Portal</title>
    <style>
        body {
            font-family: Arial;
            margin: 0;
            background: #f0f2f5;
        }
        .app-container {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 1rem;
        }
        .main-content {
            display: flex;
            flex: 1;
            padding: 20px;
        }
        .sidebar {
            width: 200px;
            background: white;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }
        .content-area {
            flex: 1;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }
        .login-container {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        .input-wrapper {
            position: relative;
        }
        .input-wrapper input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .input-wrapper i {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #666;
        }
        .btn {
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn-primary {
            background: #3498db;
            color: white;
        }
        .btn-primary:hover {
            background: #2980b9;
        }
        .loading {
            display: none;
            margin-left: 10px;
        }
        .error-message {
            color: red;
            margin-top: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <header class="header">
            <h1>Enterprise Portal</h1>
        </header>

        <div class="main-content">
            <aside class="sidebar">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="#" id="help-link">Help</a></li>
                    <li><a href="#" id="contact-link">Contact</a></li>
                </ul>
            </aside>

            <main class="content-area">
                <div class="login-container">
                    <h2 id="form-title">Authentication Required</h2>
                    <form id="login-form" class="auth-form">
                        <div class="form-group">
                            <label for="username">Username or Email:</label>
                            <div class="input-wrapper">
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    class="form-control"
                                    data-testid="username-input"
                                    autocomplete="off"
                                >
                            </div>
                            <div class="error-message" id="username-error"></div>
                        </div>

                        <div class="form-group">
                            <label for="password">Password:</label>
                            <div class="input-wrapper">
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    class="form-control"
                                    data-testid="password-input"
                                >
                            </div>
                            <div class="error-message" id="password-error"></div>
                        </div>

                        <div class="form-group">
                            <button type="submit" id="login-button" class="btn btn-primary">
                                <span class="button-text">Sign In</span>
                                <span class="loading">...</span>
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    </div>

    <script>
        // Simulate complex UI changes and dynamic behavior
        setTimeout(() => {
            // Change form structure and attributes
            document.getElementById('username').setAttribute('data-testid', 'email-input');
            document.getElementById('password').setAttribute('data-testid', 'pwd-input');

            // Change IDs
            document.getElementById('username').id = 'email';
            document.getElementById('password').id = 'pwd';
            document.getElementById('login-button').id = 'submit-auth';

            // Change text content
            document.querySelector('.button-text').textContent = 'Authenticate';
            document.querySelector('#form-title').textContent = 'Login Required';

            // Add new elements
            const rememberMe = document.createElement('div');
            rememberMe.className = 'form-group';
            rememberMe.innerHTML = `
                <label>
                    <input type="checkbox" id="remember" name="remember">
                    Remember me
                </label>
            `;
            document.querySelector('form').insertBefore(
                rememberMe,
                document.querySelector('form').lastElementChild
            );

            // Change form structure
            document.querySelectorAll('.input-wrapper').forEach(wrapper => {
                const input = wrapper.querySelector('input');
                const newWrapper = document.createElement('div');
                newWrapper.className = 'field-container';
                wrapper.parentNode.replaceChild(newWrapper, wrapper);
                newWrapper.appendChild(input);
            });

            // Add dynamic validation
            document.querySelectorAll('input').forEach(input => {
                input.addEventListener('blur', () => {
                    const errorDiv = document.getElementById(`${input.id}-error`);
                    if (errorDiv && !input.value) {
                        errorDiv.style.display = 'block';
                        errorDiv.textContent = 'This field is required';
                    }
                });
            });
        }, 5000);
    </script>
</body>
</html>''')  # Insert the HTML content here

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        smart_locator = EnhancedSmartLocator()
        file_path = os.path.abspath('complex_login.html')
        driver.get(f"file:///{file_path}")

        username = smart_locator.learn_element(driver, (By.ID, "username"), "username_field")
        password = smart_locator.learn_element(driver, (By.ID, "password"), "password_field")
        login = smart_locator.learn_element(driver, (By.ID, "login-button"), "login_button")

        time.sleep(6)

        username = smart_locator.find_element(driver, "username_field")
        password = smart_locator.find_element(driver, "password_field")
        login = smart_locator.find_element(driver, "login_button")

        ai_suggestion = get_ai_suggestion("username_field", driver.page_source)
        print("AI Suggestion:", ai_suggestion)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()
        os.remove('complex_login.html')

if __name__ == "__main__":
    main()
# in this we are matching the n-1 iteration of Locator with the nth iteration of Locator with the help of similarity between them,
# the similarity is defined on the basis of features and traits of the element.
#