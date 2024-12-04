import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta


desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
download_dir = os.path.join(desktop_dir, "MSEData")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,  #
    "safebrowsing.enabled": True,
}


options.add_argument("--headless")
options.add_argument("--disable-gpu")

options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.mse.mk/en/stats/symbolhistory/kmb"

def get_issuers():
    """Fetch issuers from the dropdown."""
    driver.get(BASE_URL)

    issuer_dropdown = driver.find_element(By.ID, "Code")
    issuer_dropdown = Select(issuer_dropdown)

    issuers = []
    for option in issuer_dropdown.options:
        issuer_code = option.get_attribute("value")
        issuer_name = option.text.strip()
        if issuer_code and not any(char.isdigit() for char in issuer_name):
            issuers.append((issuer_code, issuer_name))

    print("Issuers found:", issuers)

    # Save issuers to a JSON file
    with open(os.path.join(download_dir, "issuers.json"), "w") as f:
        json.dump(issuers, f, indent=4)

    return issuers


def wait_for_all_downloads():
    """Wait for all downloads to finish by checking the download folder."""
    timeout = 30
    start_time = time.time()

    while time.time() - start_time < timeout:
        all_downloads_complete = True
        for fname in os.listdir(download_dir):
            if fname.endswith(".crdownload"):
                print(f"Waiting for download to finish: {fname}")
                all_downloads_complete = False
                break

        if all_downloads_complete:
            return True

        time.sleep(1)

    return False


def rename_downloaded_file(issuer_name, start_date, end_date):
    """Rename the downloaded file after download is complete."""
    date_range = f"{start_date.strftime('%m-%d-%Y')}_to_{end_date.strftime('%m-%d-%Y')}"
    original_file = None

    # Check for the most recent downloaded file
    for fname in os.listdir(download_dir):
        if fname.endswith(".xls") and "Historical Data" in fname:
            original_file = fname
            break

    if original_file:
        # Replace slashes with dashes in the filename
        new_file_name = f"{issuer_name}_{date_range}.xls"
        new_file_path = os.path.join(download_dir, new_file_name)


        count = 1
        while os.path.exists(new_file_path):
            new_file_name = f"{issuer_name}_{date_range}_{count}.xls"
            new_file_path = os.path.join(download_dir, new_file_name)
            count += 1


        original_file_path = os.path.join(download_dir, original_file)
        os.rename(original_file_path, new_file_path)
        print(f"File renamed to: {new_file_name}")


def download_issuer_data(issuer_code, issuer_name):
    """Download data for a specific issuer iterating 10 years back."""
    end_date = datetime.now()
    interval_days = 365
    years_to_iterate = 10

    for year in range(years_to_iterate):
        start_date = end_date - timedelta(days=interval_days)

        driver.get(BASE_URL)


        issuer_dropdown = driver.find_element(By.ID, "Code")
        issuer_dropdown = Select(issuer_dropdown)
        issuer_dropdown.select_by_value(issuer_code)


        from_date = start_date.strftime("%m/%d/%Y")
        to_date = end_date.strftime("%m/%d/%Y")

        from_date_input = driver.find_element(By.ID, "FromDate")
        to_date_input = driver.find_element(By.ID, "ToDate")
        from_date_input.clear()
        from_date_input.send_keys(from_date)
        to_date_input.clear()
        to_date_input.send_keys(to_date)


        find_button = driver.find_element(By.CSS_SELECTOR, "#report-filter-container > ul > li.container-end > input")
        find_button.click()


        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "#resultsTable tbody tr")
            if not rows:
                print(f"No data for {issuer_name} from {from_date} to {to_date}. Skipping.")
                continue
        except Exception:
            print(f"Error checking data for {issuer_name} from {from_date} to {to_date}. Skipping.")
            continue


        download_button = driver.find_element(By.CSS_SELECTOR, "#btnExport > i")
        download_button.click()


        if wait_for_all_downloads():
            rename_downloaded_file(issuer_name, start_date, end_date)

        #
        end_date = start_date - timedelta(days=1)


def main():
    """Main function to download data for all issuers."""
    start_time = time.time()
    issuers = get_issuers()
    for issuer_code, issuer_name in issuers:
        print(f"Downloading data for issuer: {issuer_name}")
        try:
            download_issuer_data(issuer_code, issuer_name)
        except Exception as e:
            print(f"Error downloading data for issuer {issuer_name}: {e}")


    if wait_for_all_downloads():
        print("All downloads have completed.")
    else:
        print("Some downloads did not complete successfully.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProcess completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()