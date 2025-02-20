from selenium.webdriver.common.by import By
import os
import pickle
from groq import Groq

client = Groq(api_key="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")

MEMORY_FILE = "xpath_memory.pkl"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "wb") as f:
        pickle.dump(memory, f)

xpath_memory = load_memory()


def get_new_xpath_candidates(element_name):
    prompt = f"""
    The element "{element_name}" cannot be found.  
    Analyze the webpage structure and suggest the **top 3 most reliable XPaths** that can locate this element.

    **Return format:**  
    - Each XPath on a new line  
    - No explanations, just XPaths  

    **Example:**  
    ```
    //button[@id='submitBtn']
    //button[contains(text(), 'Submit')]
    //button[@class='submit-primary']
    ```
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content.strip()


        xpaths = [line.strip() for line in response.split("\n") if line.strip().startswith("//")]

        return xpaths if xpaths else None
    except Exception as e:
        return f"Failed to get a suggestion from Llama 3.3: {str(e)}"


def select_best_xpath(xpaths):
    if not xpaths or len(xpaths) == 0:
        return None

    prompt = f"""
    Here are multiple possible XPaths for a webpage element:

    ```
    {chr(10).join(xpaths)}
    ```

    **Your task:**  
    - Select **only one XPath** that is most reliable and future-proof.  
    - Return **only the XPath**, nothing else.  
    - **Do not return multiple XPaths.**  

    **Example Response:**  
    ```
    //button[@id='submitBtn']
    ```
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        selected_xpath = chat_completion.choices[0].message.content.strip()

        if "`" in selected_xpath:
            selected_xpath = selected_xpath.split("`")[1]

        return selected_xpath
    except Exception as e:
        return f"Failed to select the best XPath: {str(e)}"
def find_element_with_recovery(driver, element_name):
    possible_xpaths = [
        f"//input[@id='{element_name}']",
            f"//input[@name='{element_name}']",
            f"//input[contains(@placeholder, '{element_name.capitalize()}')]",
            f"//input[contains(@id, 'textField')]",
            f"//input[contains(@class, 'input')]",
            f"//label[contains(text(), '{element_name}')]/following-sibling::input",
            f"//div[contains(text(), '{element_name}')]/following::input[1]",
    ]

    for xpath in possible_xpaths:
        try:
            print(f"Trying default XPath: {xpath}")
            element = driver.find_element(By.XPATH, xpath)
            return element
        except:
            continue

    print(f"Element '{element_name}' not found. Requesting LLM help...")

    xpaths = get_new_xpath_candidates(element_name)
    print(f"LLM Suggested XPaths: {xpaths}")

    if not xpaths:
        print(f"LLM failed to generate XPath suggestions for '{element_name}'.")
        return None

    best_xpath = select_best_xpath(xpaths)
    print(f"Selected Best XPath: {best_xpath}")

    if not best_xpath:
        print(f"Failed to determine the best XPath for '{element_name}'.")
        return None

    try:
        print(f"Trying LLM XPath: {best_xpath}")
        element = driver.find_element(By.XPATH, best_xpath)
        print(f"Element '{element_name}' found using LLM XPath!")
        return element
    except:
        print(f"LLM recovery failed for '{element_name}'.")
        return None
