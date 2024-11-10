from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import json
import time


options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.mse.mk/en/stats/symbolhistory/kmb"


def get_issuers():
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Code")))
    issuer_dropdown = Select(driver.find_element(By.ID, "Code"))

    # fetch issuers without numbers
    issuers = []
    for option in issuer_dropdown.options:
        issuer_code = option.get_attribute("value")
        issuer_name = option.text.strip()
        if issuer_code and not any(char.isdigit() for char in issuer_name):
            issuers.append((issuer_code, issuer_name))

    print("Issuers found:", issuers)
    return issuers


def fetch_issuer_data(issuer_code, start_date, end_date):
    driver.get(BASE_URL)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Code")))

    issuer_dropdown = Select(driver.find_element(By.ID, "Code"))
    issuer_dropdown.select_by_value(issuer_code)

    from_date_input = driver.find_element(By.ID, "FromDate")
    to_date_input = driver.find_element(By.ID, "ToDate")
    from_date_input.clear()
    from_date_input.send_keys(start_date.strftime("%m/%d/%Y"))
    to_date_input.clear()
    to_date_input.send_keys(end_date.strftime("%m/%d/%Y"))

    find_button = driver.find_element(By.CSS_SELECTOR, "#report-filter-container > ul > li.container-end > input")
    find_button.click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "resultsTable")))
    except TimeoutException:
        print(f"Timeout: Results table timed out for issuer {issuer_code} from {start_date} to {end_date}")
        return []

    data = []
    rows = driver.find_elements(By.CSS_SELECTOR, "#resultsTable tbody tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        transaction = {
            "date": cells[0].text.strip() if cells[0].text.strip() else None,
            "last_trade_price": float(cells[1].text.strip().replace(",", "")) if cells[1].text.strip() else None,
            "max_price": float(cells[2].text.strip().replace(",", "")) if cells[2].text.strip() else None,
            "min_price": float(cells[3].text.strip().replace(",", "")) if cells[3].text.strip() else None,
            "avg_price": float(cells[4].text.strip().replace(",", "")) if cells[4].text.strip() else None,
            "percent_change": float(cells[5].text.strip().replace("%", "")) if cells[5].text.strip() else None,
            "volume": int(cells[6].text.strip().replace(",", "")) if cells[6].text.strip() else None,
            "turnover_in_best_denars": float(cells[7].text.strip().replace(",", "")) if cells[7].text.strip() else None,
            "total_turnover_denars": float(cells[8].text.strip().replace(",", "")) if cells[8].text.strip() else None
        }

        print("Transaction:", transaction)

        data.append(transaction)

    return data


def main():
    start_time = time.time()
    issuers = get_issuers()
    all_data = {}

    for issuer_code, issuer_name in issuers:
        print(f"Collecting data for issuer: {issuer_name}")
        issuer_data = []
        end_date = datetime.now()

        # iterating 10 years back, 11 days at a time
        for _ in range(365 * 10 // 11):
            start_date = end_date - timedelta(days=11)
            try:
                data_chunk = fetch_issuer_data(issuer_code, start_date, end_date)
                issuer_data.extend(data_chunk)
            except Exception as e:
                print(f"Error fetching data for issuer {issuer_name} from {start_date} to {end_date}: {e}")
            end_date = start_date - timedelta(days=1)

        all_data[issuer_name] = issuer_data

    # save to json
    with open("mse_data.json", "w") as f:
        json.dump(all_data, f, indent=4)
    print("Data collection complete. Saved to mse_data.json")

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
