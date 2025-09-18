from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import os
import time
import random

def setup_driver():
    """Set up Chrome WebDriver with headless configuration."""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def convert_lot_size_to_sqft(lot_size):
    """Convert lot_size from acres to sqft if in float format with 'acres'."""
    if lot_size is None:
        return None
    lot_size_lower = lot_size.lower()
    lot_size_clean = lot_size_lower.replace(",", "").replace("sq ft", "").replace("acres", "").strip()
    try:
        value = float(lot_size_clean)
        return str(int(value * 43560)) if "acres" in lot_size_lower else str(int(value))
    except ValueError:
        return lot_size_clean

def save_to_csv(df, output_file, listing_data, processed_urls):
    """Append a single listing to DataFrame and CSV if not a duplicate."""
    if listing_data["url"] in processed_urls:
        print(f"Skipping duplicate: {listing_data['url']}")
        return df, processed_urls

    # Add to df
    new_row_df = pd.DataFrame([listing_data])
    df = pd.concat([df, new_row_df], ignore_index=True)

    # Append only the new row to CSV
    header = not os.path.exists(output_file)
    new_row_df.to_csv(output_file, mode='a', index=False, header=header)

    processed_urls.add(listing_data["url"])
    print(f"Saved data for {listing_data['address']} to {output_file}")
    return df, processed_urls

def scrape_redfin_listing(driver, url):
    """Scrape house listing data from a single URL."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bp-AddressBannerSectionV2"))
        )

        listing_data = {
            "address": None,
            "price": None,
            "est_monthly_payment": None,
            "bedrooms": None,
            "bathrooms": None,
            "square_footage": None,
            "property_type": None,
            "year_built": None,
            "lot_size": None,
            "price_per_sqft": None,
            "parking": None
        }
        
        # Extract address
        try:
            address = driver.find_element(By.CLASS_NAME, "street-address").text
            city_state_zip = driver.find_element(By.CLASS_NAME, "bp-cityStateZip").text
            listing_data["address"] = f"{address} {city_state_zip}"
        except NoSuchElementException:
            pass

        # Extract price
        try:
            listing_data["price"] = driver.find_element(By.CLASS_NAME, "statsValue.price").text.replace(",", "").replace("$", "").strip()
        except NoSuchElementException:
            pass

        # Extract estimated monthly payment
        try:
            payment = driver.find_element(By.CLASS_NAME, "monthly-payment").text
            listing_data["est_monthly_payment"] = payment.replace("Est. ", "").replace("/mo", "").replace("$", "").strip()
        except NoSuchElementException:
            pass

        # Extract bedrooms
        try:
            listing_data["bedrooms"] = driver.find_element(By.CLASS_NAME, "stat-block.beds-section").find_element(By.CLASS_NAME, "statsValue").text
        except NoSuchElementException:
            pass

        # Extract bathrooms
        try:
            listing_data["bathrooms"] = driver.find_element(By.CLASS_NAME, "stat-block.baths-section").find_element(By.CLASS_NAME, "bath-flyout").text.replace(" ba", "").strip()
        except NoSuchElementException:
            pass

        # Extract square footage
        try:
            listing_data["square_footage"] = driver.find_element(By.CLASS_NAME, "stat-block.sqft-section").find_element(By.CLASS_NAME, "statsValue").text.replace(",", "").strip()
        except NoSuchElementException:
            pass

        # Extract key details
        for detail in driver.find_elements(By.CLASS_NAME, "keyDetails-row"):
            try:
                label = detail.find_element(By.CLASS_NAME, "valueType").text.strip().rstrip(":")
                value = detail.find_element(By.CLASS_NAME, "valueText").text.strip()
                if label == "Property Type":
                    listing_data["property_type"] = value
                elif label == "Year Built":
                    listing_data["year_built"] = value
                elif label == "Lot Size":
                    listing_data["lot_size"] = convert_lot_size_to_sqft(value)
                elif label == "Price/Sq.Ft.":
                    listing_data["price_per_sqft"] = value.replace("$", "").strip()
                elif label == "Parking":
                    listing_data["parking"] = value.replace("cars", "").replace("garage", "").replace("spaces", "").replace("car", "").replace("space", "").strip()
            except NoSuchElementException:
                continue

        return listing_data

    except TimeoutException:
        print(f"Error: Page took too long to load for {url}")
        return None
    except Exception as e:
        print(f"Error for {url}: {str(e)}")
        return None

def scrape_city_listings(city_url, city_name, df, output_file, processed_urls, state):
    """Scrape all house listings for a city across all pages."""
    driver = setup_driver()
    page = 1
    max_pages = 10

    try:
        while page <= max_pages:
            url = city_url if page == 1 else f"{city_url}/page-{page}"
            print(f"Scraping page {page} for {city_name}: {url}")
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bp-Homecard"))
            )

            house_urls = {
                card.get_attribute("href") for card in driver.find_elements(By.CLASS_NAME, "bp-Homecard")
                if card.get_attribute("href") and card.get_attribute("href").startswith("https://www.redfin.com/WA/")
            }  # Use set to avoid duplicates within a page

            if not house_urls:
                print(f"No listings found on page {page} for {city_name}. Stopping.")
                break

            print(f"Found {len(house_urls)} unique house URLs on page {page} for {city_name}")

            for house_url in house_urls:
                if house_url in processed_urls:
                    print(f"Skipping duplicate house URL: {house_url}")
                    continue
                print(f"Scraping house: {house_url}")
                listing_data = scrape_redfin_listing(driver, house_url)
                if listing_data:
                    listing_data["state"] = state
                    listing_data["city"] = city_name
                    listing_data["url"] = house_url
                    df, processed_urls = save_to_csv(df, output_file, listing_data, processed_urls)
                    time.sleep(random.uniform(0.5, 1.5))

            page += 1
            time.sleep(random.uniform(0.5, 1.5))

    except TimeoutException:
        print(f"Error: Page {page} took too long to load for {city_name}")
    except Exception as e:
        print(f"Error on page {page} for {city_name}: {str(e)}")
    finally:
        driver.quit()

    return df, processed_urls

def scrape_mississippi_listings(base_url):
    """Scrape house listings for all Mississippi cities."""
    columns = ["state", "city", "address", "price", "est_monthly_payment", "bedrooms", "bathrooms",
               "square_footage", "property_type", "year_built", "lot_size", "price_per_sqft", "parking","url"]
    output_file = "data/house_listings.csv"

    # Load existing data if CSV exists
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        processed_urls = set(df["url"].dropna().tolist())
    else:
        df = pd.DataFrame(columns=columns)
        processed_urls = set()

    driver = setup_driver()
    try:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filterableTable"))
        )

        # Extract city URLs
        city_data = [
            (row.find_element(By.CLASS_NAME, "Cities").find_element(By.TAG_NAME, "a").text,
             row.find_element(By.CLASS_NAME, "Cities").find_element(By.TAG_NAME, "a").get_attribute("href"))
            for row in driver.find_elements(By.CSS_SELECTOR, "tr[class^='tl']")
            if row.find_element(By.CLASS_NAME, "Cities").find_elements(By.TAG_NAME, "a")
        ]

        print(f"Found {len(city_data)} city URLs")

        state = "Washington"
        for city_name, city_url in city_data:
            print(f"Processing city: {city_name} ({city_url})")
            df, processed_urls = scrape_city_listings(city_url, city_name, df, output_file, processed_urls, state)
            time.sleep(random.uniform(2, 4))

        print(f"Scraping complete. Data saved to {output_file}")
        return df

    except TimeoutException:
        print("Error: State page took too long to load")
        return df
    except Exception as e:
        print(f"Error on state page: {str(e)}")
        return df
    finally:
        driver.quit()

if __name__ == "__main__":
    base_url = "https://www.redfin.com/state/Washington"
    scrape_mississippi_listings(base_url)