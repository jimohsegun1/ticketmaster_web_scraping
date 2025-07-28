# Ticketmaster Web Scraper:
 - website: https://www.ticketmaster.com/broadway

A Python-based scraper for extracting Broadway show events from Ticketmaster. This project uses Selenium with undetected-chromedriver to navigate the dynamic site in real time, scrapes all the shows date one after the other and shows, event data, deduplicates it using hashes, and stores it in MongoDB and also include scraping logs. It supports email and Slack notifications for scraping status and results.

---

### OVERVIEW:
- Technologies
- Features
- Additional Features slack and email notification, data saved to MongoDB
- Folder structure
- Setup the project
- Running the project
- To view the MongoDB saved datas in terminal

## Technologies:
    - BeautifulSoup + request
    - Selenium e.t.c

## Features:
- Scrapes Broadway show details including Show Title, Show date, Show img link, Theatre Name/venue, Performance, Show Type (e.g., Musical, Play), Link to full show details
- Uses undetected ChromeDriver to bypass bot detection.
- Logs the process in the log folder to see the runtime 
- while you run the project it start crawling and scraping of the website on realtime
- Deduplicates events using MD5 hashes to avoid duplicate entries in MongoDB
- Saves scraped data to JSON and CSV files.
- Notification or Reporting sends an email and slack message to the Awarri's random channel when new shows are detected and when scraping starts.
- Supports scheduled scraping every 5 hours using the `schedule` library.
- CLI tool to view latest events from MongoDB. with python cli_viewer.py --limit 5
- Validation script to check stored data integrity.with python validate_mongo.py

---

## Additional Features slack and email notification, data saved to MongoDB:
- created slack notification to `Awarri's` `# random` slack channel with the app named `Demo App`
- Also created email notification
- Data saved to MongoDB

## Folder structure:
```
assessement_scraping
├──.venv/           # installed modules folder
├── config.py       # Configuration loader using environment variables
├── cli_viewer.py        # CLI script to view events from MongoDB
├── data/       # Folder to store JSON and CSV output files
├── log/        # Folder to store scraping logs
├── requirements.txt    # Python dependencies
├── scrape.py       # Main scraper script
├── validate_mongo.py       # Script to validate MongoDB data
├── .env        # Environment variables (not committed)
└── README.md       # Project documentation
```
# Check the data folder for the csv and json files named with dates and time 
---

## Setup the project:

- Clone the project
- Create a `.env` file in the root directory with the following variables (example values) for email and slack notification and saving data to mongoDB:
```
MONGO_URI=your_mongodb_connection_string
MONGO_DB=ticketmaster
MONGO_COLLECTION=broadway_events

EMAIL_ENABLED=True

EMAIL_SENDER=youremail@example.com
EMAIL_RECEIVER=receiveremail@example.com

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

EMAIL_USERNAME=youremail@example.com
EMAIL_PASSWORD=your_email_password_or_app_specific_password

SLACK_ENABLED=True
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

---

## Running the project:

- in your terminal navigate to your root and 
    - run: `pip install -r requirements.txt` to install dependencies 
    - run: `python onetime.py --once` to run once 
    ### or 
    - run: `python onetime.py` scheduler to run the scraper at scheduled defined intervals (6 hours):
    ### after running these operations will start:
	- Launch a Chrome browser with undetected driver.
	- Scrape Broadway shows and their event dates.
	- Save results as JSON and CSV in the data/ folder.
	- Log activities in the log/ folder.
	- Store new events in MongoDB.
	- Send email and Slack notifications.
    - Run once or either schedule based on the script you run

#### To view the MongoDB saved datas in terminal, run:
`python cli_viewer.py --limit 5`      - Show 5 latest events

`python cli_viewer.py --all`        - Show all events

`python validate_mongo.py`     - connects to MongoDB and prints the total number of events along with a few sample event details.


