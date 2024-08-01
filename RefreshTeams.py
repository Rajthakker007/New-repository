import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the directory containing the Chrome WebDriver executable to the PATH environment variable
chromedriver_path = 'C:/Drivers/chromedriver-win64/chromedriver-win64/chromedriver'
os.environ['PATH'] += os.pathsep + chromedriver_path

# Specify the path to the Chrome user data directory containing the "bhavani 1st" profile
chrome_options = Options()
chrome_options.add_argument('--user-data-dir=C:/Users/lovet/AppData/Local/Google/Chrome/User Data/bhavani 1st')
chrome_options.add_argument('--no-sandbox')  # Required for Linux

# URL of the webpage to refresh
url = 'https://teams.microsoft.com/v2/'

# Initialize Chrome webdriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Open the webpage
driver.get(url)

# Continuous refresh loop
while True:
    # Refresh the webpage
    driver.refresh()
    print("Page refreshed at", time.strftime("%Y-%m-%d %H:%M:%S"))

    # Wait for 5 minutes before refreshing again
    time.sleep(300)  # 300 seconds = 5 minutes

# Close the webdriver (unreachable due to infinite loop)
# driver.quit()