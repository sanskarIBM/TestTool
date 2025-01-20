from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from bs4 import BeautifulSoup
import json
import re
import time

from webdriver_manager.chrome import ChromeDriverManager


# Function to initialize WebDriver for Safari
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re
import time
from webdriver_manager.chrome import ChromeDriverManager

# Function to initialize WebDriver for Chrome
def get_driver():
    """
    Initializes and returns a Selenium WebDriver instance for Chrome.
    """
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver



# Function to scrape elements on the page
def scroll_and_capture_page_source(driver):
    """
    Scrolls the page incrementally to load all dynamic content and returns the full page source.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial page height

    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new content to load

        # Get the new height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Check if the page height hasn't changed (indicating the end of the page)
        if new_height == last_height:
            break
        last_height = new_height  # Update the last height

    # Return the fully loaded page source
    return driver.page_source


# Updated capture_elements_on_page to include scrolling
def capture_elements_on_page(driver, url):
    """
    Scrapes all input and button elements on a given page, including dynamic content loaded via scrolling.
    """
    print(f"Scraping URL: {url}")
    driver.get(url)
    time.sleep(5)  # Wait for the initial page to load

    # Scroll the page to load all dynamic content
    page_source = scroll_and_capture_page_source(driver)
    soup = BeautifulSoup(page_source, "html.parser")
    elements_attributes = []

    # Scrape input and button elements
    for element in soup.find_all(['input', 'button']):
        label = soup.find('label', {'for': element.get('id')})
        label_text = label.get_text(strip=True) if label else None
        if label_text:
            label_text = re.sub(r'\s+', ' ', label_text).strip()
        element_attributes = {
            "label": label_text,
            "tag_name": element.name,
            "id": element.get('id'),
            "class": ' '.join(element.get('class', [])),
            "name": element.get('name'),
            "type": element.get('type') if element.name == 'input' else None,
            "text": element.get_text(strip=True) if element.name == 'button' else None,
            "all_xpaths": generate_all_xpaths(soup, element, label_text),
            "css_selector": f"#{element.get('id')}" if element.get('id') else None
        }
        # Filter out attributes with None values and add to the results
        element_attributes = {k: v for k, v in element_attributes.items() if v}
        if "id" in element_attributes or element.name == "button":  # Ensure button elements without IDs are included
            elements_attributes.append(element_attributes)

    return {"page_url": url, "elements": elements_attributes}



# Function to generate all possible XPath combinations
def generate_all_xpaths(soup, element, label_text=None):
    """
    Generates all possible XPath combinations for a given element, including label-based XPaths.
    """
    xpaths = []
    attributes = element.attrs
    element_tag = element.name

    # 1. ID-based XPath (if available)
    if 'id' in attributes:
        xpaths.append(f"//*[@id='{attributes['id']}']")

    # 2. Class-based XPath (if available)
    if 'class' in attributes:
        class_conditions = [f"contains(@class, '{cls}')" for cls in attributes['class']]
        xpaths.append(f"{element_tag}[{' and '.join(class_conditions)}]")

    # 3. Name-based XPath
    if 'name' in attributes:
        xpaths.append(f"{element_tag}[@name='{attributes['name']}']")

    # 4. Type-based XPath
    if 'type' in attributes:
        xpaths.append(f"{element_tag}[@type='{attributes['type']}']")

    # 5. Label-based XPath (using `contains(text(), '<label_text>')`)
    if label_text:
        xpaths.append(f"//label[contains(text(), '{label_text}')]//{element_tag}")

    # 6. Combination of attributes (e.g., id + class, name + type)
    if 'id' in attributes and 'class' in attributes:
        class_conditions = [f"contains(@class, '{cls}')" for cls in attributes['class']]
        xpaths.append(f"//*[@id='{attributes['id']}' and {' and '.join(class_conditions)}]")

    if 'name' in attributes and 'type' in attributes:
        xpaths.append(f"{element_tag}[@name='{attributes['name']}' and @type='{attributes['type']}']")

    # 7. Text-based XPath (for non-input elements with visible text)
    if element_tag not in ['input', 'textarea'] and element.get_text(strip=True):
        text_content = element.get_text(strip=True)
        xpaths.append(f"{element_tag}[contains(text(), '{text_content[:15]}')]")

    # 8. Positional XPath (Fallback)
    siblings = element.find_parent().find_all(element_tag, recursive=False)
    if len(siblings) > 1:
        index = siblings.index(element) + 1
        xpaths.append(f"{element_tag}[{index}]")

    # 9. Parent-child hierarchy XPath
    hierarchy_xpath = []
    child = element
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) > 1:
            hierarchy_xpath.append(f'{child.name}[{siblings.index(child) + 1}]')
        else:
            hierarchy_xpath.append(child.name)
        child = parent
        if parent.name == 'html':
            break
    hierarchy_xpath.reverse()
    xpaths.append('/' + '/'.join(hierarchy_xpath))

    # Return all unique XPaths
    return list(set(xpaths))  # Deduplicate for safety


# Function to save data to JSON
def save_to_json(data, file_name):
    """
    Saves the provided data to a JSON file.
    """
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# Main function
def main():
    # List of websites to scrape
    websites = [
        "http://books.toscrape.com/",
        "https://amazon.in/"
    ]

    driver = get_driver()
    try:
        for website in websites:
            scraped_data = capture_elements_on_page(driver, website)
            file_name = website.split("//")[-1].replace("/", "_") + ".json"
            save_to_json(scraped_data, file_name)
            print(f"Scraped data from {website} saved to '{file_name}'")
    except Exception as e:
        print("Error during scraping:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()