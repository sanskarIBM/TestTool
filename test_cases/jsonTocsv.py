from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
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

# Function to scroll and load all dynamic content
def scroll_and_capture_page_source(driver):
    """
    Scrolls the page incrementally to load all dynamic content and returns the full page source.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial page height

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom
        time.sleep(5)  # Wait for content to load
        new_height = driver.execute_script("return document.body.scrollHeight")  # Get new height
        if new_height == last_height:  # Break if no new content is loaded
            break
        last_height = new_height

    return driver.page_source

# Function to generate all possible XPath combinations for an element
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

# Function to capture elements on a page and extract XPaths
def capture_elements_on_page(driver, url):
    """
    Scrapes all input and button elements on a given page, including dynamic content loaded via scrolling.
    """
    print(f"Scraping URL: {url}")
    driver.get(url)
    time.sleep(5)  # Wait for initial page load
    page_source = scroll_and_capture_page_source(driver)
    soup = BeautifulSoup(page_source, "html.parser")

    xpaths = []  # Store all unique XPaths
    for element in soup.find_all(['input', 'button']):
        label = soup.find('label', {'for': element.get('id')})
        label_text = label.get_text(strip=True) if label else None
        element_xpaths = generate_all_xpaths(soup, element, label_text)
        xpaths.extend(element_xpaths)

    return xpaths

# Function to save XPaths to CSV
def save_xpaths_to_csv(xpaths, file_name):
    """
    Saves a list of XPaths to a CSV file.
    """
    with open(file_name, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["XPath"])  # Header row
        for xpath in xpaths:
            csv_writer.writerow([xpath])
    print(f"Saved XPaths to '{file_name}'")

# Main function
def main():
    # List of websites to scrape
    # websites = [
    #     "http://books.toscrape.com/",
    #     "https://amazon.in/",
    #     "https://flipkart.com/",
    #     "https://www.youtube.com/",
    #     "https://www.myntra.com/"
    # ]
    websites = [
        "http://books.toscrape.com/",
        "https://amazon.in/",
        "https://flipkart.com/",
        "https://www.youtube.com/",
        "https://www.myntra.com/",
        "https://www.ebay.com/",
        "https://www.target.com/",
        "https://www.walmart.com/",
        "https://www.bestbuy.com/",
        "https://www.apple.com/",
        "https://www.microsoft.com/",
        "https://www.netflix.com/",
        "https://www.spotify.com/",
        "https://www.airbnb.com/",
        "https://www.booking.com/",
        "https://www.expedia.com/",
        "https://www.zomato.com/",
        "https://www.swiggy.com/",
        "https://www.udemy.com/",
        "https://www.coursera.org/",
        "https://www.linkedin.com/",
        "https://www.instagram.com/",
        "https://www.facebook.com/",
        "https://www.twitter.com/",
        "https://www.reddit.com/"
    ]

    driver = get_driver()
    try:
        all_xpaths = []  # Collect XPaths from all websites
        for website in websites:
            website_xpaths = capture_elements_on_page(driver, website)
            all_xpaths.extend(website_xpaths)

        # Save all XPaths to a single CSV file
        save_xpaths_to_csv(all_xpaths, "xpathsData.csv")
    except Exception as e:
        print("Error during scraping:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
