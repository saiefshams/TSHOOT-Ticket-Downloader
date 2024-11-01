import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# osTicket credentials
username = 'your_username'
password = 'your_password'

# osTicket URLs
base_url = 'http://tshoot2.networkinglab.local/scp'

# Define days
days = {
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday"
}
# Variations
variations = ["a", "b"]

# Download path
download_path = '''specify download path here. for example:''' "C:\\Users\\username\\Downloads"

# Prompt for lab number
lab_number = input("Please provide the lab number (e.g., 3): ")

# Create folders
for day in days.values():
    for y in variations:
        folder_name = f"Lab{lab_number}{y} {day}"
        folder_path = os.path.join(download_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")

# Prompt for ticket number ranges
ticket_ranges = {}
for day in days.values():
    for y in variations:
        key = f"Lab{lab_number}{y} {day}"
        ticket_ranges[key] = input(f"Please provide ticket # range for {key} (e.g., 369-469): ")

# Set up a Chrome WebDriver instance with modified profile settings
chrome_options = Options()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-site-isolation-trials")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Log in to osTicket
login_url = f'{base_url}/login.php'
driver.get(login_url)

print("Logging in to osTicket...")
try:
    userid_field = driver.find_element(By.NAME, 'userid')
    passwd_field = driver.find_element(By.NAME, 'passwd')
    submit_button = driver.find_element(By.NAME, 'submit')
    
    userid_field.send_keys(username)
    passwd_field.send_keys(password)
    submit_button.click()
    print("Login submitted.")
    time.sleep(1)  # Wait for the login to process
    
    # Ensure login success
    if "Authentication Required" in driver.page_source or driver.current_url == login_url:
        print("Login failed. Please check your username and password.")
        driver.quit()
        exit()
    else:
        print("Login successful.")
except Exception as e:
    print(f"Error during login: {e}")
    driver.quit()
    exit()

# Function to wait for downloads to complete
def wait_for_downloads(directory, filename, timeout=60):
    file_path = os.path.join(directory, filename)
    print(f"Waiting for download to complete: {file_path}")
    start_time = time.time()
    while True:
        if os.path.isfile(file_path):
            # Check if the file's modification time has stopped changing
            initial_mtime = os.path.getmtime(file_path)
            time.sleep(1)
            if os.path.getmtime(file_path) == initial_mtime:
                print(f"Download complete: {file_path}")
                return
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for download: {file_path}")
            return
        time.sleep(1)

# Function to download attachments
def download_attachment(ticket_id, lab_number, pod, y, day):
    url_id = int(ticket_id) + 300  # Adjusting for the offset
    ticket_url = f'{base_url}/tickets.php?id={url_id}'
    driver.get(ticket_url)
    print(f"Navigating to: {ticket_url}")

    try:
        # Locate and download the attachment from the ticket response
        response_entries = driver.find_elements(By.CSS_SELECTOR, 'div.thread-entry.response')
        for entry in response_entries:
            attachment_links = entry.find_elements(By.CSS_SELECTOR, 'a.filename')
            for attachment_link in attachment_links:
                attachment_url = attachment_link.get_attribute('href')
                original_filename = attachment_link.get_attribute('download')
                print(f"Found attachment: {original_filename}")

                # Set the download directory to the correct folder
                download_directory = os.path.join(download_path, f"Lab{lab_number}{y} {day}")
                prefs["download.default_directory"] = download_directory
                chrome_options.add_experimental_option("prefs", prefs)
                driver.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': download_directory})

                # Use JavaScript to click the attachment link
                driver.execute_script("arguments[0].click();", attachment_link)
                print(f"Downloading {original_filename}...")

                # Wait for download to complete
                wait_for_downloads(download_directory, original_filename)
                print(f"Confirmed download of {original_filename}.")

                # Rename the file
                new_filename = f"s{lab_number}p{pod}.pdf"
                os.rename(os.path.join(download_directory, original_filename), os.path.join(download_directory, new_filename))
                print(f"Renamed {original_filename} to {new_filename}.")
    except Exception as e:
        print(f"No attachment found for ticket {ticket_id}. Error: {e}")

# Download files based on provided ticket ranges
for key, ticket_range in ticket_ranges.items():
    start, end = map(int, ticket_range.split('-'))
    y = key[4]        # Extracts variation from key
    day = key.split()[-1] # Extracts day from key
    
    for ticket_id in range(start, end + 1):
        padded_ticket_id = f'{ticket_id:06}'  # Ensuring the ticket ID is 6 digits
        pod = ticket_id - start + 1
        download_attachment(padded_ticket_id, lab_number, pod, y, day)

driver.quit()

print("All files downloaded and organized successfully!")