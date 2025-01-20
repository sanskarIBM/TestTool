from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import difflib
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from typing import List, Tuple, Dict


class SmartLocatorStrategy:
    def __init__(self):
        # Initialize BERT model for semantic similarity
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')

        # Historical locator mappings
        self.locator_history = {}

    def _get_parent_structure(self, element, depth=3) -> List[Dict]:
        """
        Get the structure of parent elements up to specified depth

        Args:
            element: WebElement to analyze
            depth: How many levels up to traverse (default: 3)

        Returns:
            List of dictionaries containing parent elements' information
        """
        structure = []
        current = element

        for _ in range(depth):
            try:
                parent = current.find_element(By.XPATH, "..")
                parent_info = {
                    'tag_name': parent.tag_name,
                    'class': parent.get_attribute('class'),
                    'id': parent.get_attribute('id'),
                    'relative_position': {
                        'x': parent.location['x'] - current.location['x'],
                        'y': parent.location['y'] - current.location['y']
                    }
                }
                structure.append(parent_info)
                current = parent
            except:
                break

        return structure

    def get_element_signature(self, element) -> Dict:
        """Extract various attributes and surrounding context of an element"""
        return {
            'tag_name': element.tag_name,
            'text': element.text,
            'attributes': {
                name: element.get_attribute(name)
                for name in ['class', 'id', 'name', 'type', 'value', 'href', 'src']
                if element.get_attribute(name)
            },
            'location': element.location,
            'size': element.size,
            'parent_structure': self._get_parent_structure(element)
        }

    def _get_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using BERT embeddings"""
        if not text1 or not text2:
            return 0.0

        # Tokenize texts
        inputs1 = self.tokenizer(text1, return_tensors='pt', padding=True, truncation=True)
        inputs2 = self.tokenizer(text2, return_tensors='pt', padding=True, truncation=True)

        # Get embeddings
        with torch.no_grad():
            embeddings1 = self.model(**inputs1).last_hidden_state.mean(dim=1)
            embeddings2 = self.model(**inputs2).last_hidden_state.mean(dim=1)

        # Calculate cosine similarity
        similarity = torch.nn.functional.cosine_similarity(embeddings1, embeddings2)
        return similarity.item()

    def _calculate_structure_similarity(self, sig1: Dict, sig2: Dict) -> float:
        """Calculate similarity score between two element signatures"""
        score = 0.0

        # Compare tag names
        if sig1['tag_name'] == sig2['tag_name']:
            score += 0.2

        # Compare text content semantically
        if sig1['text'] and sig2['text']:
            score += 0.3 * self._get_semantic_similarity(sig1['text'], sig2['text'])

        # Compare attributes
        common_attrs = set(sig1['attributes'].keys()) & set(sig2['attributes'].keys())
        if common_attrs:
            attr_similarity = sum(difflib.SequenceMatcher(None,
                                                          str(sig1['attributes'][attr]),
                                                          str(sig2['attributes'][attr])).ratio()
                                  for attr in common_attrs) / len(common_attrs)
            score += 0.3 * attr_similarity

        # Compare relative position
        position_diff = abs(sig1['location']['x'] - sig2['location']['x']) + \
                        abs(sig1['location']['y'] - sig2['location']['y'])
        score += 0.2 * (1 / (1 + position_diff / 100))

        return score

    def find_element(self, driver, original_locator: Tuple[By, str]):
        """Find element using smart locator strategy"""
        try:
            # First try the original locator
            element = driver.find_element(*original_locator)
            return element
        except NoSuchElementException:
            # If original locator fails, try to find the most similar element
            if original_locator in self.locator_history:
                original_signature = self.locator_history[original_locator]

                # Get all potential elements
                all_elements = driver.find_elements(By.XPATH, "//*")

                best_match = None
                best_score = 0

                for element in all_elements:
                    try:
                        current_signature = self.get_element_signature(element)
                        similarity_score = self._calculate_structure_similarity(
                            original_signature, current_signature)

                        if similarity_score > best_score and similarity_score > 0.8:  # Threshold
                            best_score = similarity_score
                            best_match = element
                    except:
                        continue

                if best_match:
                    # Update locator history with new signature
                    self.locator_history[original_locator] = self.get_element_signature(best_match)
                    return best_match

            raise NoSuchElementException(
                f"Could not find element with locator {original_locator}")

    def learn_element(self, driver, locator: Tuple[By, str]):
        """Learn and store element signature for future reference"""
        element = driver.find_element(*locator)
        self.locator_history[locator] = self.get_element_signature(element)


def example_usage():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        smart_locator = SmartLocatorStrategy()

        # Navigate to LinkedIn login page
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)  # Wait for page to load

        # Define locators for key elements
        username_locator = (By.ID, "username")
        password_locator = (By.ID, "password")
        login_button_locator = (By.XPATH, "//button[@type='submit']")

        # Learn all the original elements
        smart_locator.learn_element(driver, username_locator)
        smart_locator.learn_element(driver, password_locator)
        smart_locator.learn_element(driver, login_button_locator)

        # Find elements using smart locator
        username_field = smart_locator.find_element(driver, username_locator)
        password_field = smart_locator.find_element(driver, password_locator)
        login_button = smart_locator.find_element(driver, login_button_locator)

        print("Successfully found all elements!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    example_usage()