from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv

# Function to set up Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
    return driver

# Function to scrape city list from state page
def get_cities(driver, state_url):
    driver.get(state_url)
    time.sleep(3)  # Wait for page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cities = []
    
    table = soup.find('table', class_='filterableTable')
    if table:
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            city_cell = row.find('td', class_='c0')
            if city_cell:
                a_tag = city_cell.find('a')
                if a_tag:
                    city_name = a_tag.text
                    city_href = a_tag['href']
                    cities.append((city_name, city_href))
    
    return cities

# Function to scrape houses from a city page, handling pagination
def scrape_city_houses(driver, city_url):
    houses = []
    page = 1
    while True:
        current_url = city_url if page == 1 else f"{city_url}/page-{page}"
        driver.get(current_url)
        time.sleep(3)  # Wait for page to load
        # Scroll to bottom to load all content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        house_cards = soup.find_all('a', class_='bp-Homecard')
        if not house_cards:
            break  # No more houses
        
        for card in house_cards:
            house_href = card.get('href')
            if house_href:
                houses.append(house_href)
        
        page += 1
        time.sleep(2)  # Delay to avoid rate limiting
    
    return houses

# Function to scrape details from a house page
def scrape_house_details(driver, house_url):
    driver.get(house_url)
    time.sleep(3)  # Wait for page to load
    # Scroll to load all sections
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    details = {}
    
    # Address
    address_elem = soup.find('div', class_='bp-homeAddress')
    if address_elem:
        details['address'] = address_elem.text.strip()
    
    # Price
    price_elem = soup.find('div', {'data-rf-test-id': 'abp-price'})
    if price_elem:
        details['price'] = price_elem.find('div', class_='statsValue').text.strip()
    
    # Beds
    beds_elem = soup.find('div', {'data-rf-test-id': 'abp-beds'})
    if beds_elem:
        details['beds'] = beds_elem.find('div', class_='statsValue').text.strip()
    
    # Baths
    baths_elem = soup.find('div', class_='stat-block baths-section')
    if baths_elem:
        details['baths'] = baths_elem.find('span', class_='statsLabel').text.strip()  # e.g., "2 ba"
    
    # Sq Ft
    sqft_elem = soup.find('div', {'data-rf-test-id': 'abp-sqFt'})
    if sqft_elem:
        details['sqft'] = sqft_elem.find('span', class_='statsValue').text.strip()
    
    # Key Details Table
    key_table = soup.find('div', class_='KeyDetailsTable')
    if key_table:
        rows = key_table.find_all('div', class_='keyDetails-row')
        for row in rows:
            value_div = row.find('div', class_='keyDetails-value')
            if value_div:
                value_text_span = value_div.find('span', class_='valueText')
                value_type_span = value_div.find('span', class_='valueType')
                if value_text_span and value_type_span:
                    key = value_type_span.text.strip().lower().replace(' ', '_').replace('.', '')
                    val = value_text_span.text.strip()
                    details[key] = val
    
    # Amenities sections for HOA and Parking
    amenity_groups = soup.find_all('div', class_='amenity-group')
    amenities = {}
    for group in amenity_groups:
        title_div = group.find('div', class_='title')
        if title_div:
            section = title_div.text.strip()
            ul = group.find('ul')
            if ul:
                items = [li.text.strip() for li in ul.find_all('li')]
                amenities[section] = items
    
    # Parking
    details['parking'] = ''
    if 'Parking Information' in amenities:
        details['parking'] = ', '.join(amenities['Parking Information'])
    
    # HOA
    details['hoa'] = ''
    sections_for_hoa = ['HOA / Condo / Coop', 'Community Information', 'Association Fee Information', 'Association Information']
    for sec in sections_for_hoa:
        if sec in amenities:
            items = amenities[sec]
            for item in items:
                if any(term in item for term in ['HOA Fee', 'Dues', 'Association Fee']):
                    details['hoa'] += item + ' '
    details['hoa'] = details['hoa'].strip()
    
    return details

# Main function
def main():
    base_url = 'https://www.redfin.com'
    state_url = base_url + '/state/Mississippi'
    
    driver = setup_driver()
    try:
        cities = get_cities(driver, state_url)
        if not cities:
            print("No cities found.")
            return
        
        all_houses = []
        
        for city_name, city_href in cities:
            city_url = base_url + city_href
            print(f"Scraping city: {city_name} ({city_url})")
            
            house_hrefs = scrape_city_houses(driver, city_url)
            for house_href in house_hrefs:
                house_url = base_url + house_href
                print(f"Scraping house: {house_url}")
                details = scrape_house_details(driver, house_url)
                if details:
                    all_houses.append(details)
                    print(details)
                time.sleep(2)  # Delay between house requests
        
        # Parse city and state from address and save to CSV
        columns = ["Property-Type", "Year-Built", "Lot-Size", "Square-Feet", "Bedrooms", "Bathrooms", "Price", "Address", "City", "State", "On-Redfin", "Price/Sq.Ft.", "HOA", "Parking"]
        with open('mississippi_houses.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for house in all_houses:
                address = house.get('address', '')
                city = ''
                state = ''
                full_address = address
                if address:
                    parts = address.split(', ')
                    if len(parts) >= 3:
                        full_address = parts[0]
                        city = parts[1]
                        state_zip = parts[2].split(' ')
                        if len(state_zip) >= 2:
                            state = state_zip[0]
                
                row = {
                    "Property-Type": house.get('property_type', ''),
                    "Year-Built": house.get('year_built', ''),
                    "Lot-Size": house.get('lot_size', ''),
                    "Square-Feet": house.get('sqft', ''),
                    "Bedrooms": house.get('beds', ''),
                    "Bathrooms": house.get('baths', ''),
                    "Price": house.get('price', ''),
                    "Address": full_address,
                    "City": city,
                    "State": state,
                    "On-Redfin": house.get('on_redfin', ''),
                    "Price/Sq.Ft.": house.get('price/sqft', ''),
                    "HOA": house.get('hoa', ''),
                    "Parking": house.get('parking', '')
                }
                writer.writerow(row)
        print("Data saved to mississippi_houses.csv")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()