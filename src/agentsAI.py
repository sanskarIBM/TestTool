import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# def get_ai_suggestion(locator): # for invalid locator
    # prompt = (
    #     f"Error: NoSuchElementException. "
    #     f"Current locator used: {locator}. "
    #     f"Please suggest only the most accurate and optimal locator to resolve this issue. "
    #     f"Ensure the locator is in the exact format: tagname[attribute='value'], no additional text or explanation."
    # )
def get_ai_suggestion(locator_text, html_source):
    prompt = (
        f"Error: NoSuchElementException encountered while trying to interact with an element containing the text: '{locator_text}'. "
        f"The following is the HTML structure of the page:\n\n"
        f"{html_source}\n\n"
        f"Using the provided HTML, suggest a simple, reliable, and valid CSS Selector for identifying the dynamic element related to this text. "
        f"Please suggest a general CSS selector (avoid overly specific or complicated ones). "
        f"Avoid using invalid CSS patterns such as `>`, `contains`, or `text()`. "
        f"Return a clean, straightforward CSS selector like `tagname[attribute='value']`, `tagname.classname`, or `tagname#id`. "
        f"Ensure it is a valid, simple selector that will work for this element in the provided HTML."
        f"Do not include any additional text or explanation—strictly return the CSS Selector."
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
