import cloudscraper
from bs4 import BeautifulSoup
import csv
import os
import time
import random

# URL of the page with the table
url = "https://fintables.com/sirketler/A1CAP/finansal-tablolar/bilanco"

# Create a scraper instance
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

try:
    # Add a random delay to avoid rate limiting
    time.sleep(random.uniform(2, 5))
    
    print("Attempting to fetch the page...")
    response = scraper.get(url, timeout=30)
    
    # Print response details for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    # Check if the page was fetched successfully
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # Print first 500 chars of response
        exit()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element (adjust the selector if needed)
    table = soup.find("table")
    if not table:
        print("No table found on the page.")
        print("Page content preview:", soup.prettify()[:500])  # Print first 500 chars of parsed content
        exit()

    # Extract headers from the first row (assuming the first <tr> contains headers)
    header_row = table.find("tr")
    headers_list = [header.get_text(strip=True) for header in header_row.find_all(["th", "td"])]

    # Extract data rows (skip the header row)
    data_rows = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if cells:
            row_data = [cell.get_text(strip=True) for cell in cells]
            data_rows.append(row_data)

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Write the data into a CSV file
    csv_filename = "output/bilanco.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers_list)
        writer.writerows(data_rows)

    print(f"Table data has been written to {csv_filename}")
    print(f"Number of rows processed: {len(data_rows)}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit()
