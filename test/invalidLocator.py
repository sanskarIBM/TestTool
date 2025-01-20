from selenium import webdriver

# Initialize the WebDriver
driver = webdriver.Chrome()

# Navigate to the desired URL
driver.get("https://myntra.com")

# Execute JavaScript to get the outerHTML of the entire document
page_source = driver.execute_script("return document.documentElement.outerHTML;")
with open("page_source.html", "w", encoding="utf-8") as file:
    file.write(page_source)
# Print the collected DOM
print(page_source)


# Close the driver
driver.quit()