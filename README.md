# Automatic Ticket Downloader v1
This script automates the process of downloading attachments from osTicket tickets and organizing them into specific folders based on lab numbers, variations (Lab a or b), and Sections.


### Prerequisites
Before you start, make sure you have the following installed:
- Python 3.x (this code was written and tested on 3.12)
- pip (Python package installer)


### Installation Process
1. Clone the repository (if you haven't already):
  ```
  git clone https://github.com/saiefshams/TSHOOT-Ticket-Downloader
  cd TSHOOT-Ticket-Downloader
  ```
2. Install the required Python packages:
  ```
  pip install -r requirements.txt
  ```


###Configuring the script
- Set your osTicket credentials:
Open the automaticTicketDownloader.py file and replace 'your_username' and 'your_password' with your actual osTicket username and password.
```
username = 'your_username'
password = 'your_password'
```
- Set the base URL for osTicket:
Ensure the base_url variable is set to the correct URL for your osTicket instance.
```base_url = 'http://tshoot2.networkinglab.local/scp'```
- Set the download path:
Specify the path where you want the downloaded files to be saved.
```download_path = "C:\\Users\\username\\Downloads"```


### Running the Script
- Run the script:
```python automaticTicketDownloader.py```
- Provide the lab number:
When prompted, enter the lab number (e.g., 3).
```Please provide the lab number (e.g., 3):```
- Provide ticket number ranges:
For each combination of lab number, ticket variation (a or b), and Section, you will be prompted to enter the ticket number range (e.g., 369-469).
```
Please provide ticket # range for Lab3a Tuesday (e.g., 369-469):
Please provide ticket # range for Lab3a Wednesday (e.g., 369-469):
Please provide ticket # range for Lab3a Thursday (e.g., 369-469):
Please provide ticket # range for Lab3b Tuesday (e.g., 369-469):
Please provide ticket # range for Lab3b Wednesday (e.g., 369-469):
Please provide ticket # range for Lab3b Thursday (e.g., 369-469):
```


### How It Works

#### Setup:

The script starts by creating folders for each combination of lab number, variation, and section. Next, the script sets up a Chrome WebDriver instance with specific profile settings to handle downloads. Then the script logs in to osTicket using the provided credentials.
For each ticket in the specified ranges, the script navigates to the ticket URL, finds the attachment links, and downloads the attachments. The script then waits for the downloads to complete by checking the file's modification time. 
The script iterates through the provided ticket ranges and downloads the attachments for each ticket. Finally, the script quits the WebDriver instance and prints a success message.


### Demo:
https://github.com/user-attachments/assets/e505b3f6-1bce-407e-b050-53c35e230f72


### Upcoming Changes:
##### Version 2:
Version 2 will have more input sanitization and prompt the user to choose the download directory instead of hardcoding it in the script.
