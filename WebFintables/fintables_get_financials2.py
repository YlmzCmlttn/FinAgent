import cloudscraper
import json
import csv

def fetch_html(url):
    """
    Uses cloudscraper to fetch the HTML content from the URL.
    Returns the HTML text on success, or None if failed.
    """
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows"
        }
    )
    print(f"Fetching URL: {url}")
    response = scraper.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. HTTP status code: {response.status_code}")
        return None
    return response.text

def extract_sheet_data(html_text):
    """
    Searches the HTML text for a JSON object that follows the marker
    '"sheetType":"bilanco","data":'
    and returns the parsed Python object.
    
    It does so by finding the position of the marker, then locating the first
    '{', and balancing the braces to extract the entire JSON object.
    """
    marker = '"sheetType":"bilanco","data":'
    marker_index = html_text.find(marker)
    if marker_index == -1:
        print("Could not locate the 'sheetType':'bilanco' marker in the HTML.")
        return None

    # Move index to the beginning of the JSON data
    start = marker_index + len(marker)
    # Skip any whitespace until we find the opening brace
    while start < len(html_text) and html_text[start] not in '{':
        start += 1
    if start >= len(html_text):
        print("Could not find the start of the JSON data after the marker.")
        return None

    # Use a simple brace-balancing method to find the matching closing brace.
    brace_count = 0
    end = start
    while end < len(html_text):
        if html_text[end] == '{':
            brace_count += 1
        elif html_text[end] == '}':
            brace_count -= 1
            if brace_count == 0:
                end += 1  # include the closing brace
                break
        end += 1

    json_str = html_text[start:end]
    try:
        data_obj = json.loads(json_str)
        print("Successfully extracted sheet data JSON.")
        return data_obj
    except json.JSONDecodeError as e:
        print("Error parsing sheet data JSON:", e)
        return None

def save_financial_data_to_csv(financial_items, csv_filename):
    """
    Saves the provided financial items to a CSV file.
    
    Each row in the CSV will contain:
       - The financial item title (from the "title" key)
       - The sequential numerical values from its "values" array.
       
    If an item has fewer values than the maximum among all items,
    its row will be padded with empty strings.
    """
    if not financial_items:
        print("No financial items to save.")
        return

    # Determine the maximum length of the 'values' arrays for header consistency.
    max_values = max(len(item.get("values", [])) for item in financial_items)
    header = ['title'] + [f'value_{i+1}' for i in range(max_values)]
    
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for item in financial_items:
                title = item.get("title", "")
                values = item.get("values", [])
                # Convert numeric values to string; use empty string for None.
                row_values = [str(v) if v is not None else "" for v in values]
                # Pad the values list so all rows have the same number of columns.
                if len(row_values) < max_values:
                    row_values.extend([""] * (max_values - len(row_values)))
                writer.writerow([title] + row_values)
        print(f"Financial data successfully saved to '{csv_filename}'.")
    except Exception as e:
        print("Error writing CSV:", e)

def main():
    # Set the stock symbol and build the URL.
    stock_name = "KCHOL"
    url = f"https://fintables.com/sirketler/{stock_name}/finansal-tablolar/bilanco?period=&type=&currency=&mode=unadjusted"
    
    # Fetch the HTML from the URL.
    html_text = fetch_html(url)
    if html_text is None:
        return

    # Try to extract the sheet data JSON from the HTML.
    sheet_data = extract_sheet_data(html_text)
    if sheet_data is None:
        print("No sheet data extracted.")
        return

    # The extracted sheet_data should be a dictionary containing a key "data"
    # which holds the array of financial items.
    financial_items = sheet_data.get("data")
    if not financial_items:
        print("No financial items found in the extracted sheet data.")
        return

    # Save the financial items to a CSV file.
    csv_filename = f"{stock_name}_financial_data.csv"
    save_financial_data_to_csv(financial_items, csv_filename)

if __name__ == '__main__':
    main()
