import cloudscraper
from bs4 import BeautifulSoup
import csv
import os
import time
import random

stock_name = "A1CAP"
# URL of the page with the table
url = f"https://fintables.com/sirketler/{stock_name}/finansal-tablolar/bilanco?period=&type=&currency=&mode=unadjusted"

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
    
    # Check if the page was fetched successfully
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # Print first 500 chars of response
        exit()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all table rows
    rows = soup.find_all("tr")
    
    # Initialize lists to store data
    data_rows = []
    current_section = ""
    
    # Process each row
    for row in rows:
        # Get all cells in the row
        cells = row.find_all(["td", "th"])
        
        if not cells:
            continue
            
        # Get the first cell (label)
        label = cells[0].get_text(strip=True)
        
        # Check if this is a section header
        if label in ["Dönen Varlıklar", "Duran Varlıklar", "Kısa Vadeli Yükümlülükler", 
                    "Uzun Vadeli Yükümlülükler", "Özkaynaklar"]:
            current_section = label
            continue
            
        # Get values from other cells
        values = []
        for cell in cells[1:]:
            # Find all spans with tabular-nums class
            value_spans = cell.find_all("span", class_="tabular-nums")
            if value_spans:
                # Get the last span which contains the main value
                main_value = value_spans[-1].get_text(strip=True)
                # Remove any non-numeric characters except decimal point
                main_value = ''.join(c for c in main_value if c.isdigit() or c == '.')
                values.append(main_value)
            else:
                values.append("")
        
        # Add the row data with section
        if values:
            row_data = [current_section, label] + values
            data_rows.append(row_data)

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Write the data into a CSV file
    csv_filename = f"output/{stock_name}_bilanco.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header
        #writer.writerow(["Section", "Item", "2024/12", "2024/9", "2024/6", "2024/3", "2023/12"])
        # Write data rows
        writer.writerows(data_rows)

    print(f"Table data has been written to {csv_filename}")
    print(f"Number of rows processed: {len(data_rows)}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit()
