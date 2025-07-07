from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def scrape_countries():
    # Step 1: Open Chrome in headless (no-browser) mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # Step 2: Go to the webpage
    driver.get("https://www.scrapethissite.com/pages/simple/")  # Replace with real site
    time.sleep(2)  # Wait a bit for the page to load

    # Step 3: Find all the country blocks
    countries = driver.find_elements(By.CLASS_NAME, "country")

    # Step 4: Create a list to store each country's data
    country_data_list = []

    # Step 5: Loop through and collect data
    for country in countries:
        name = country.find_element(By.CLASS_NAME, "country-name").text
        capital = country.find_element(By.CLASS_NAME, "country-capital").text
        population = country.find_element(By.CLASS_NAME, "country-population").text
        area = country.find_element(By.CLASS_NAME, "country-area").text

        country_data = {
            "Name": name,
            "Capital": capital,
            "Population": population,
            "Area": area
        }

        country_data_list.append(country_data)

        
    # Step 6: Close the browser
    driver.quit()

    # Step 7: Print the data
    for country in country_data_list:
        print(country)

    # save it in .json
    with open('countries_data.json', 'w') as f:
        import json
        json.dump(country_data_list, f, indent=4)


    return country_data_list

if __name__ == "__main__":
    scrape_countries()
    print("Scraping completed and data saved to countries_data.json")