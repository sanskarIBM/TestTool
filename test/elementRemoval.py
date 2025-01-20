from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import numpy as np


def extract_ids_and_text_from_html(html):
    """Extract IDs and associated text from the HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    elements = []
    for element in soup.find_all(attrs={"type": True}):
        element_type = element.get('type', '')
        element_text = element.get_text(strip=True) or ''
        elements.append({'type': element_type, 'text': element_text})
    return elements


def get_embedding(text, model):
    """Generate an embedding for a given text using an NLP model."""
    return model.encode(text, convert_to_tensor=True)


def find_best_match(prev_id, elements, model):
    """Find the best matching element based on semantic similarity."""
    prev_embedding = get_embedding(prev_id, model)

    best_match = None
    highest_similarity = -1

    for element in elements:
        combined_text = f"{element['type']} {element['text']}"  # Combine ID and text for context
        element_embedding = get_embedding(combined_text, model)
        similarity = util.pytorch_cos_sim(prev_embedding, element_embedding).item()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = element['text']

    return best_match


def suggest_replacement_locator(prev_locator, driver, model):
    """Suggest a replacement locator using NLP-based semantic matching."""
    try:
        # Extract the previous ID from the locator
        prev_id = prev_locator.split('=')[-1].strip('"').strip(']')

        # Get current page source and extract all IDs and text
        html = driver.page_source
        elements = extract_ids_and_text_from_html(html)

        # Find the best match using semantic similarity
        best_match = find_best_match(prev_id, elements, model)

        # Return the new XPath if a match is found
        if best_match:
            return f"//button[contains(text(), '{best_match}')]"
        else:
            return None
    except Exception as e:
        print(f"Error during replacement suggestion: {e}")
        return None


# Example Usage
if __name__ == "__main__":
    # Initialize the NLP model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize WebDriver
    driver = webdriver.Chrome()
    driver.get("http://books.toscrape.com/")

    # Previous failing locator
    # prev_locator = '//*[@id="username"]'
    prev_locator = "//button[contains(text(), 'Add to cart')]"
    # Suggest a replacement
    new_locator = suggest_replacement_locator(prev_locator, driver, model)
    if new_locator:
        print(f"Suggested Locator: {new_locator}")
        try:
            # Try using the new locator
            element = driver.find_element(By.XPATH, new_locator)
            element.click()
            print("Test passed with new locator!")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("No suitable replacement locator found.")
    driver.quit()
