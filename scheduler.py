

def run_scraper():
    import undetected_chromedriver as uc 
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    import time
    import pandas as pd
    from bs4 import BeautifulSoup
    from datetime import datetime

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...')

    driver = uc.Chrome(options=options)
    driver.maximize_window()
    driver.get('https://www.ticketmaster.com/broadway')

    soup = BeautifulSoup(driver.page_source, 'lxml')
    bs = soup.find_all('div', class_='card item ny-category-musicals ny')

    links = []
    for item in bs:
        lk = item.find('a').get('href') if item.find('a') else ''
        name = item.find('h3').text.strip() if item.find('h3') else ''
        img = item.find('img').get('src') if item.find('img') else ''
        links.append({'Name': name, 'Link': lk, 'Image url': img})

    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    details = []

    for entry in links:
        url = entry['Link']
        driver.get(url)
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pageInfo"]/div[1]/ul/li[1]/button'))).click()
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

                details.append({
                    'Scrape Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Show': entry['Name'],
                    'Link': url,
                    'Image Url': entry['Image url'],
                    'Theatre': thea.text.strip() if thea else '',
                    'Date': date.text.strip() if date else '',
                    'Time': time_.text.strip() if time_ else '',
                    'Location': loc.text.strip() if loc else ''
                })

            try:
                more_events_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='More Events']/ancestor::button"))
                )
                actions.move_to_element(more_events_button).perform()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='More Events']/ancestor::button"))).click()
                time.sleep(2)
            except:
                break

    driver.quit()
    df = pd.DataFrame(details)
    filename = f"event_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
    
    # Deduplicate across all files
    import os
    
    existing_data = pd.concat([
        pd.read_excel(f) for f in os.listdir() 
        if f.startswith("event_details_") and f.endswith(".xlsx")
    ], ignore_index=True)
    
    combined = pd.concat([existing_data], ignore_index=True)
    combined.drop_duplicates(subset=['Show', 'Date', 'Time'], inplace=True)
    combined.to_excel("event_details_deduped.xlsx", index=False)




import schedule
import time

schedule.every(24).hours.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(60)
