import os
import time
import json
import subprocess
from tkinter import Tk
from tkinter.filedialog import askdirectory
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Check if config.json exists
config_file_path = 'config.json'
if not os.path.exists(config_file_path):
    # Run config_setup.py if config.json does not exist
    print("config.json not found. Running config_setup.py to create the file.")
    subprocess.run(['python', 'config_setup.py'])

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    username = config['username']
    password = config['password']
    base_url = config['base_url']
    sections = config['sections']

# Prompt user to select download directory
print("Initializing Tkinter...")
root = Tk()
root.withdraw()
# Use Ctrl+Tab to find the tkinter file explorer window if it doesn't appear on top
print("Opening directory selection dialog...")
download_path = askdirectory(title="Select Download Directory")
if not download_path:
    print("No directory selected. Exiting.")
    exit()

# Print the selected download directory for verification
print(f"Selected download directory: {download_path}")

# Ensure the download path uses the correct format
download_path = download_path.replace("/", "\\")

# Print the formatted download directory for verification
print(f"Formatted download directory: {download_path}")

# Function to get valid integer input
def get_valid_int_input(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                print(f"Please enter a value between {min_value} and {max_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

# Function to get valid string input
def get_valid_str_input(prompt, valid_values=None):
    while True:
        value = input(prompt).strip()
        if valid_values and value not in valid_values:
            print(f"Invalid input. Please enter one of the following: {', '.join(valid_values)}")
        else:
            return value

# Prompt for lab number
lab_number = get_valid_int_input("Please provide the lab number (e.g., 3): ", min_value=1)

# Prompt for number of variations
num_variations = get_valid_int_input("Please provide the number of variations (e.g., 2): ", min_value=1)
variations = [chr(97 + i) for i in range(num_variations)]  # Generate variations like ['a', 'b']

# Create folders
for section, details in sections.items():
    day = details['day']
    for y in variations:
        folder_name = f"Lab{lab_number}{y} {day}"
        folder_path = os.path.join(download_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")

# Prompt for ticket number ranges
ticket_ranges = {}
for section, details in sections.items():
    day = details['day']
    for y in variations:
        while True:
            try:
                ticket_range = input(f"Please provide the ticket number range for Lab{lab_number}{y} {day} (e.g., 100-200): ")
                # Split the input into start and end numbers
                start, end = map(int, ticket_range.split('-'))
                # Ensure the start number is less than or equal to the end number
                if start > end:
                    print("Invalid range. Start number should be less than or equal to end number.")
                # Ensure the range is valid
                else:
                    ticket_ranges[f"Lab{lab_number}{y} {day}"] = (start, end)
                    break
            except ValueError:
                print("Invalid input. Please enter a valid range in the format 'start-end'.")

# Set up a Chrome WebDriver instance with modified profile settings
chrome_options = Options()
# Set the download directory and disable download prompt
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
# Add additional options to bypass security warnings (not recommended for general use, only because the tickets are hosted on a local server and its not https)
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-site-isolation-trials")
# Initialize the Chrome WebDriver instance
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Log in to osTicket
login_url = f'{base_url}/login.php'
driver.get(login_url)

print("Logging in to osTicket...")
try:
    # Locate the login fields and submit button
    userid_field = driver.find_element(By.NAME, 'userid')
    passwd_field = driver.find_element(By.NAME, 'passwd')
    submit_button = driver.find_element(By.NAME, 'submit')
    # Enter the login credentials and submit
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
    # Handle login errors
    print(f"Error during login: {e}")
    driver.quit()
    exit()

# Initialize counters and lists for statistics
attachments_downloaded = 0
pdf_downloaded = 0
docx_downloaded = 0
other_downloaded = 0
tickets_no_attachments = 0
tickets_multiple_attachments = 0
tickets_no_attachments_list = []
tickets_multiple_attachments_list = []
tickets_no_responses_list = []
invalid_tickets_list = []

# Function to get section and pod information
def get_section_pod_info():
    try:
        # First, try to get the section and pod information from response entries
        section_pod_elements = driver.find_elements(By.CSS_SELECTOR, 'div.thread-entry.response .header b')
        for element in section_pod_elements:
            text = element.text
            if "Section" in text and "Pod" in text:
                return text
        # If no response entries are found, try to get the information from thread events
        section_pod_elements = driver.find_elements(By.CSS_SELECTOR, 'div.thread-event .faded.description b')
        for element in section_pod_elements:
            text = element.text
            if "Section" in text and "Pod" in text:
                return text
    except Exception as e:
        print(f"Error extracting section and pod information: {e}")
    return "Unknown Section Pod"

# Function to download attachments from the latest response
def download_attachment(ticket_id, lab_number, pod, y, day):
    # Use global variables to track statistics and lists
    global attachments_downloaded, pdf_downloaded, docx_downloaded, other_downloaded, tickets_no_attachments, tickets_multiple_attachments, tickets_no_responses_list, invalid_tickets_list
    url_id = int(ticket_id) + 300  # Adjusting for the offset
    ticket_url = f'{base_url}/tickets.php?id={url_id}'
    driver.get(ticket_url)
    print(f"Navigating to: {ticket_url}")
    # Wait for the ticket page to load
    try:
        # Check for "Unknown or invalid ID" response
        if "ticket: Unknown or invalid ID." in driver.page_source:
            print(f"Ticket {ticket_id} is invalid.")
            invalid_tickets_list.append(f"Ticket {ticket_id} - Unknown Section Pod")
            return "invalid"
        # Locate and download the attachment from the latest response
        response_entries = driver.find_elements(By.CSS_SELECTOR, 'div.thread-entry.response')
        print(f"Debug: response_entries length is {len(response_entries)}")
        if response_entries:
            latest_entry = response_entries[-1]  # Get the latest response entry
            print(f"Found {len(response_entries)} response entries, using the latest one.")
            if len(response_entries) > 1:
                tickets_multiple_attachments += 1
                tickets_multiple_attachments_list.append(ticket_id)
                print(f"Ticket {ticket_id} has multiple responses, downloading the latest one.")
            # Check the latest response for attachments
            attachment_links = latest_entry.find_elements(By.CSS_SELECTOR, 'a.filename')
            if not attachment_links:
                # Check previous responses if the latest one has no attachment
                for entry in reversed(response_entries[:-1]):
                    attachment_links = entry.find_elements(By.CSS_SELECTOR, 'a.filename')
                    if attachment_links:
                        print(f"Found attachment in an earlier response for ticket {ticket_id}.")
                        break
            # Check if attachments are found
            print(f"Debug: attachment_links length is {len(attachment_links)}")
            if attachment_links:
                for attachment_link in attachment_links:
                    attachment_url = attachment_link.get_attribute('href')
                    original_filename = attachment_link.get_attribute('download')
                    print(f"Found attachment: {original_filename} at URL: {attachment_url}")

                    # Set the download directory to the correct folder
                    download_directory = os.path.join(download_path, f"Lab{lab_number}{y} {day}")
                    print(f"Setting download directory to: {download_directory}")

                    # Ensure the download directory exists
                    if not os.path.exists(download_directory):
                        os.makedirs(download_directory)
                        print(f"Created download directory: {download_directory}")

                    prefs["download.default_directory"] = download_directory
                    chrome_options.add_experimental_option("prefs", prefs)

                    # Verify if the directory is being set correctly
                    print(f"Prefs: {prefs}")

                    driver.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': download_directory})
                    print("Download behavior set")

                    # Add a delay to ensure settings take effect
                    time.sleep(2)

                    # Use JavaScript to click the attachment link
                    driver.execute_script("arguments[0].click();", attachment_link)
                    print(f"Downloading {original_filename}...")

                    # Capture browser logs immediately after attempting the download
                    logs = driver.get_log('browser')
                    for log in logs:
                        print(f"Browser log: {log}")

                    # Wait for download to complete
                    wait_for_downloads(download_directory, original_filename)
                    print(f"Confirmed download of {original_filename}.")
                    attachments_downloaded += 1

                    # Determine the file extension
                    file_extension = os.path.splitext(original_filename)[1]
                    if file_extension.lower() == '.pdf':
                        pdf_downloaded += 1
                    elif file_extension.lower() == '.docx':
                        docx_downloaded += 1
                    else:
                        other_downloaded += 1

                    # Rename the file
                    section_pod_info = get_section_pod_info()
                    new_filename = f"s{section_pod_info.split()[1]}p{pod}{file_extension}"
                    print(f"Renaming {os.path.join(download_directory, original_filename)} to {os.path.join(download_directory, new_filename)}")
                    os.rename(os.path.join(download_directory, original_filename), os.path.join(download_directory, new_filename))
                    print(f"Renamed {original_filename} to {new_filename}.")
            else:
                # No attachments found in the latest response
                print(f"No attachments found in the latest response for ticket {ticket_id}.")
                tickets_no_attachments += 1
                section_pod_info = get_section_pod_info()
                tickets_no_attachments_list.append(f"Ticket {ticket_id} - {section_pod_info}")
        else:
            # No response entries found for the ticket
            print(f"No response entries found for ticket {ticket_id}.")
            tickets_no_attachments += 1
            section_pod_info = get_section_pod_info()
            tickets_no_responses_list.append(f"Ticket {ticket_id} - {section_pod_info}")
    except Exception as e:
        # Error handling for downloading attachments
        print(f"No attachment found for ticket {ticket_id}. Error: {e}")
        tickets_no_attachments += 1
        section_pod_info = get_section_pod_info()
        tickets_no_attachments_list.append(f"Ticket {ticket_id} - {section_pod_info}")
    return "valid"


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


# Download files based on provided ticket ranges
for key, ticket_range in ticket_ranges.items():
    start, end = ticket_range
    y = key[4]        # Extracts variation from key
    day = key.split()[-1] # Extracts day from key
    
    for ticket_id in range(start, end + 1):
        padded_ticket_id = f'{ticket_id:06}'  # Ensuring the ticket ID is 6 digits
        pod = ticket_id - start + 1
        status = download_attachment(padded_ticket_id, lab_number, pod, y, day)
        if status == "invalid":
            invalid_tickets_list.append(f"Ticket {padded_ticket_id} - Unknown Section Pod")

driver.quit()

# Print statistics
print("\nDownload Summary:")
print(f"Total attachments downloaded: {attachments_downloaded}")
print(f"Total PDF files downloaded: {pdf_downloaded}")
print(f"Total DOCX files downloaded: {docx_downloaded}")
print(f"Total other files downloaded: {other_downloaded}")
print(f"Total tickets with no attachments: {tickets_no_attachments}")
print(f"Total tickets with multiple responses (latest downloaded): {tickets_multiple_attachments}")

print("\nTickets with no attachments:")
print("\n".join(tickets_no_attachments_list))

print("\nTickets with no responses:")
print("\n".join(tickets_no_responses_list))

print("\nTickets with multiple responses (latest downloaded):")
print("\n".join(tickets_multiple_attachments_list))

print("All files downloaded and organized successfully!")