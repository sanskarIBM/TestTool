from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
import groq
import logging

# Initialize Groq API Client
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = groq.Client(api_key=groq_api_key)

class DriverFactory:
    @staticmethod
    def get_driver():
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")

        # Initialize ChromeDriver using webdriver-manager (no need to specify path)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    @staticmethod
    def quit_driver(driver):
        if driver:
            driver.quit()

    @staticmethod
    def suggest_fix(error_message, locator):
        """
        Uses Groq LLM API to analyze the Selenium error and suggest fixes.

        Args:
            error_message (str): The Selenium error message.
            locator (dict): The locator details, e.g., {"type": "name", "value": "username"}.

        Returns:
            str: Suggested fix from Groq's LLM.
        """
        prompt = (
            f"I encountered a Selenium error: '{error_message}'. "
            f"The locator used was: {locator}. Suggest better strategies or locators."
        )

        try:
            response = groq_client.generate(
                prompt=prompt,
                model="groq-llm-v1",  # Replace with the appropriate Groq model name
                max_tokens=100,
            )
            return response.get("text", "").strip()
        except Exception as e:
            return f"Failed to get a suggestion from Groq: {str(e)}"

