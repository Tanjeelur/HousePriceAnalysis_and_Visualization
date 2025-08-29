import pandas as pd 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

 
# def get_data():
    

url = 'https://www.redfin.com/WA/Seattle/3915-S-Brandon-St-98118/home/172833'
# Set up the Selenium WebDriver (make sure to specify the correct path to your chromedriver)

element = {}
driver = webdriver.Chrome(service=Service('chromedriver.exe'))
driver.get(url)
# Wait for the page to load
# driver.implicitly_wait(10)
# Find the elements containing the data
property_elements = driver.find_elements(By.CLASS_NAME, 'valueText')


# Extract the text from the elements
property_elements = [element for element in property_elements]
# Close the driver
element['Property-Type']= property_elements[1].text
element['Year-Built']= property_elements[2].text
element['Lot-Size']= property_elements[3].text
element['Square-Feet']= property_elements[4].text
element['Price']= driver.find_element(By.CLASS_NAME, 'price').text
# for idx, ele in enumerate(property_elements):
#     if idx in [1,2,3,4,5,6,7]:
#         element[columns[idx-1]] = ele.text
    
print('element:', element)

driver.quit()
# Print the extracted data
