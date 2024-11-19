# Automatic Ticket Downloader v2
This script automates the process of downloading attachments from osTicket tickets and organizing them into specific folders based on lab numbers, variations (Lab a or b), and Sections.
There is a demo video at the bottom of this readme file. You can watch it to understand how the program works.


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


### Configuring the script
#### If you're running this program for the first time, you will have to set up some configurations before you can proceed.

- Set up the `config.json` file:
Run the `config_setup.py` file, and enter your username and password. The password filed uses a `getpass` module so it won't be visible on the CLI while you type it.

- Set the base URL for osTicket:
Ensure the base_url variable is set to the correct URL for your osTicket instance.
```base_url = 'http://tshoot2.networkinglab.local/scp'```

- Follow the prompts, and create the Sections and Subsections according to the semester schedule.

- Ensure a `config.json` file gets created and confirm your settings are set correctly.

- Alternatively, you can also run the `automaticTicketDownloader.py` file and it will invoke the `config_setup.py` file if it doesn't find the json.


### Running the Script
- Run the script:
```python3 automaticTicketDownloader.py```

- Select the download directory:
A Tkinter file dialog will appear. Select the directory where you want the downloaded files to be saved.

- Provide the lab number:
When prompted, enter the lab number (e.g., 3).
```Please provide the lab number (e.g., 3):```

- Provide Lab variations:
Enter the variations for the particular lab. Select 1 if there's only an "a" variant, or 2 if there are two variants, "a" and "b"

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

The script starts by importing necessary modules and checking if `config.json` exists. If not, it runs `config_setup.py` to create it. The script loads the configuration from `config.json`, including osTicket credentials, base URL, and sections. Then, the script uses Tkinter to prompt the user to select a download directory. After that, the script sets up a Chrome WebDriver instance with specific profile settings to handle downloads. The script logs in to osTicket using the provided credentials. For each ticket in the specified sections, the script navigates to the ticket URL, finds the attachment links, and downloads the attachments. The script waits for the downloads to complete by checking the file's modification time. Finally, the script quits the WebDriver instance and prints a success message.


### Demo:
https://youtu.be/oWkD_SGlVog
