import pytest

from selenium_country_scraper import scrape_countries

# Test 1: Check the scraper gives back a list with data
def test_scraper_returns_list():
    data = scrape_countries()
    assert isinstance(data, list)  # Is it a list?
    assert len(data) > 0           # Is the list not empty?

# Test 2: Check that the first country has expected values
def test_first_country_data():
    data = scrape_countries()
    first = data[0]

    # Update values if needed — this depends on the actual website content
    assert first["Name"] == "Andorra"
    assert first["Capital"] == "Andorra la Vella"

# Test 3: Check that each value is the correct type
def test_field_types():
    data = scrape_countries()
    first = data[0]

    assert isinstance(first["Name"], str)
    assert isinstance(first["Capital"], str)
    assert isinstance(first["Population"], str)  # or int depending on your data
    assert isinstance(first["Area"], str)        # or float if converted