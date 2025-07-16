from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import os
import time

def wait_for_downloads(download_directory, timeout=300):
    start_time = time.time()
    while True:
        if all(not fname.endswith('.crdownload') for fname in os.listdir(download_directory)):
            break
        elif time.time() - start_time > timeout:
            print("Timed out waiting for downloads to finish.")
            break
        time.sleep(1)

#check for popup
def check_and_close_popup(driver):
    try:
        decline_button = driver.find_element(By.CLASS_NAME, "fsrDeclineButton")
        if decline_button.is_displayed():  # Check if the button is displayed
            decline_button.click()
            print("Declined the popup invitation.")
    except NoSuchElementException:
        pass

def scrape_sec_complaints():

    download_directory = "data/sec_complaints"

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  
    })

    chrome_driver_path = "/opt/homebrew/bin/chromedriver"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options) #new

    downloaded_files = []
    total_size = 0 #new 
    runs = 0
    downloads = 0
    try:
        driver.get("https://www.sec.gov/litigation/litreleases")
        while True:
            # driver.get("https://www.sec.gov/litigation/litreleases")
            check_and_close_popup(driver)
            complaint_links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'SEC Complaint')
            
            for link in complaint_links:
                complaint_url = link.get_attribute('href')
                
                if complaint_url.endswith('.pdf'):
                    driver.get(complaint_url)
                    file_name = complaint_url.split('/')[-1]
                    downloaded_files.append(file_name)
                    downloads+=1
                else:
                    print(f"Skipped non-PDF link: {complaint_url}")

            wait_for_downloads(download_directory)
            
            # Update total_size after each page of downloads
            total_size += sum(os.path.getsize(os.path.join(download_directory, f))
                            for f in downloaded_files
                            if os.path.exists(os.path.join(download_directory, f)))

            # next page using next button
            next_button = driver.find_elements(By.CSS_SELECTOR, 'a[rel="next"]')
            if next_button:
                next_button[0].click()
                time.sleep(2)
            else:
                break  

    finally:
        # driver.quit()
        print("Stopped")

    # Output the results
    print(f"Total size of downloaded PDFs: {total_size} bytes")
    print(f"Total number of downloaded files: {downloads}")

if __name__ == "__main__":

    scrape_sec_complaints()
