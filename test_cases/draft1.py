import os
from groq import Groq
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    return driver


client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def get_ai_suggestion(locator_x, locator_type, testCode, prevLocator):
    prompt = (
        f"### Title: Generate a Correct XPath Locator "
f"#### Context: "
f"Current Locator: {locator_x} "
f"Previous Locator: {prevLocator} "
f"The correct locator should pass the test case and uniquely identify the target element. "

f"#### Instructions: "
f"1. Analyze the provided current locator, previous locator, and AI-suggested locator. "
f"2. Generate a new, accurate XPath locator that: "
f"   - Correctly identifies the target element. "
# f"   - Uses stable and reliable attributes (e.g., id, name, data-*). "
f"   - Is robust against potential UI changes. "
f"   - Is concise and maintainable. "
f"3. Provide the new locator in the required format (XPath). "
f"Output Format: Return only the new XPath locator. Avoid any additional explanations or comments."

        # f"""
        # ROLE: You are a bot that is well versed in understanding the given input which includes 3 variables with names oldData, newData and seleniumCode.
        # INSTRUCTIONS: oldData and newData are array of objects which has attributes of all the elements that need to be modified. Take all the element's attributes present in oldData and newData to modify the code. Output should be in the form of object with keys seleniumCode and modifiedElements and with values as modified or updated selenium code after all modifications, elements with all the element attributes which are in oldData and also in code respectively.
        # RULES: Use oldData and newData object attributes to modify the code. After generating code validate it, it should be a selenium code in the given language, It should be in a valid syntax with semicolons and indentations. Otherwise penalize heavily.
        #
        # input: "oldData = {prevLocator} newData = {locator_x} selenium code = {testCode}"
        # output: (Output Format : Provide only the new locator in the specified format (XPath). Avoid additional explanations or comments.)"""

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

def test_dynamic_elements():
    driver = setup_driver()
    driver.get("http://books.toscrape.com/")  # Example of dynamic loading page
    locator = "//button[contains(text(), 'Add to cart')]"
    locator_type = "Text Based Xpath Locator"
    prevLocator = "//btn[contains(text(), 'Basket')]"
    testCode = "driver.find_element(By.XPATH, locator).click()"

# /html/body/div[2]/header/div/div[1]/div[2]/div/form/div[2]/div[1]/div/input
    print("\nRunning Test Case 3: Dynamic Elements.")
    try:
        driver.find_element(By.XPATH, locator).click()
        print("Test Case 3 Passed!")
    except NoSuchElementException as e:
        print(f"Error: {str(e)}")
        html_source = driver.page_source
        # Capture the relevant HTML structur
        # Trigger AI Agent for suggestion
        print("\nAI Agent: Test case failed due to No Such Element error.")
        suggested_locator = get_ai_suggestion(locator, locator_type, testCode, prevLocator)
        print(f"\nAI suggests trying a new locator: {suggested_locator}")

        try:
            # Retry with the suggested locator
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, suggested_locator)))
            dynamic_element = driver.find_element(By.XPATH, suggested_locator)
            print(f"Dynamic Element : {suggested_locator}")
            print("Test Case 3 Passed with AI suggestion!")
        except Exception as retry_error:
            print(f"Test Case 3 still failed after AI suggestion: {retry_error}")

    driver.quit()

if __name__ == "__main__":
    test_dynamic_elements()