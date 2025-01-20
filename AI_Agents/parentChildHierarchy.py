import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def get_ai_suggestion(locator, html_source):
    prompt = (
        f"Error: NoSuchElementException encountered while trying to interact with an element: '{locator}'. "
        f"The following is the HTML structure of the page:\n\n"
        f"{html_source}\n\n"
        f"Using the provided HTML, suggest a simple, reliable, and valid XPath that leverages the parent-child hierarchy for identifying the element. "
        f"Ensure the XPath follows a hierarchical structure like: `/parent/child1/child2` or similar. "
        f"Do not include any additional text or explanation—strictly return the locator only."
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
