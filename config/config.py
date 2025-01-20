import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SELENIUM_DRIVER_PATH = os.getenv("SELENIUM_DRIVER_PATH")  # Path to ChromeDriver
BASE_URL = os.getenv("BASE_URL", "http://example.com")
