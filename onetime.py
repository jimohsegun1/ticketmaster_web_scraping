import os
import time
import json
import hashlib
import logging
import schedule
import smtplib
import random
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests

from config import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION,
    EMAIL_ENABLED, EMAIL_SENDER, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT,
    EMAIL_USERNAME, EMAIL_PASSWORD,
    SLACK_ENABLED, SLACK_WEBHOOK_URL
)

# --- Setup logging ---
if not os.path.exists('log'):
    os.makedirs('log')
log_file = os.path.join('log', 'scrape.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_and_print(message):
    print(message)
    logging.info(message)

# --- MongoDB Setup ---
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# --- Notification Functions ---
def send_email(subject, body):
    if not EMAIL_ENABLED:
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        log_and_print("✅ Email notification sent.")
    except Exception as e:
        log_and_print(f"❌ Failed to send email: {e}")

def send_slack_message(message):
    if not SLACK_ENABLED:
        return
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        if response.status_code == 200:
            log_and_print("✅ Slack message sent.")
        else:
            log_and_print(f"❌ Slack message failed: {response.text}")
    except Exception as e:
        log_and_print(f"❌ Slack message error: {e}")

# --- Hash function for deduplication ---
def hash_event(event):
    return hashlib.md5(json.dumps(event, sort_keys=True).encode()).hexdigest()

# --- Scraper Logic ---
def scrape_shows():
    start_time = datetime.now()
    log_and_print("🚀 Starting Broadway Ticketmaster Scraper...")

    send_email("Scraping Started", f"Broadway scraping started at {start_time}")
    send_slack_message(f"🎭 Broadway scraping started at {start_time}")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36')

    driver = uc.Chrome(options=options)
    driver.get('https://www.ticketmaster.com/broadway')
    time.sleep(random.uniform(2, 4))

    soup = BeautifulSoup(driver.page_source, 'lxml')
    cards = soup.find_all('div', class_='card item ny-category-musicals ny')

    links = []
    for item in cards:
        name = item.find('h3').text.strip() if item.find('h3') else ''
        link = item.find('a')['href'] if item.find('a') else ''
        img = item.find('img')['src'] if item.find('img') else ''
        if link:
            links.append({'Name': name, 'Link': link, 'Image url': img})

    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    scraped_data = []

    for entry in links:
        driver.get(entry['Link'])
        time.sleep(random.uniform(2, 4))

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pageInfo"]/div[1]/ul/li[1]/button'))).click()
            time.sleep(random.uniform(2, 3))
        except:
            continue

        while True:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            events = soup.find_all('li', class_='sc-a4c9d98c-1 gmqiju')
            for event in events:
                date = event.find('div', class_='sc-d4c18b64-0 kViXXz')
                time_ = event.find('span', class_='sc-5ae165d4-1 xHFfV')
                span_tags = event.find_all('span', class_='sc-dd1f217b-6 cBubCD')
                thea = span_tags[-1] if len(span_tags) > 0 else None
                loc = span_tags[-2] if len(span_tags) > 1 else None

                show_info = {
                    'Show': entry['Name'],
                    'Link': entry['Link'],
                    'Image Url': entry['Image url'],
                    'Theatre': thea.text.strip() if thea else '',
                    'Date': date.text.strip() if date else '',
                    'Time': time_.text.strip() if time_ else '',
                    'Location': loc.text.strip() if loc else '',
                }

                hash_id = hash_event(show_info)
                show_info['_id'] = hash_id

                if not collection.find_one({'_id': hash_id}):
                    collection.insert_one(show_info)
                    scraped_data.append(show_info)

            try:
                more_events_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='More Events']/ancestor::button"))
                )
                actions.move_to_element(more_events_button).perform()
                more_events_button.click()
                time.sleep(2)
            except:
                break

    driver.quit()

    if scraped_data:
        log_and_print(f"✅ {len(scraped_data)} new events scraped and added to MongoDB.")
        send_email("New Broadway Events", f"{len(scraped_data)} new Broadway events were added.")
        send_slack_message(f"📢 {len(scraped_data)} new Broadway events scraped.")
    else:
        log_and_print("ℹ️ No new events found.")

    # Save to file
    if not os.path.exists('data'):
        os.makedirs('data')
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = f'data/events_{now}.json'
    csv_path = f'data/events_{now}.csv'

    pd.DataFrame(scraped_data).to_json(json_path, orient='records', indent=2)
    pd.DataFrame(scraped_data).to_csv(csv_path, index=False)

    log_and_print(f"📁 Data saved to {json_path} and {csv_path}")
    log_and_print("✅ Scraping finished.\n")

# --- Scheduling ---
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run scraper once and exit')
    args = parser.parse_args()

    if args.once:
        scrape_shows()
    else:
        schedule.every(6).hours.do(scrape_shows)
        log_and_print("🕒 Scheduler started. Scraper will run every 6 hours.")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()






