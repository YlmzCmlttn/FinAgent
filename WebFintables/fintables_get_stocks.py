import json

# Define input and output file names
input_filename = "stocks.json"
output_filename = "stock_codes.txt"

# Read the JSON file
with open(input_filename, "r", encoding="utf-8") as infile:
    stocks = json.load(infile)

# Extract the stock codes from the "data" list
stock_codes = [item["code"] for item in stocks.get("data", []) if "code" in item]

# Write the extracted codes to the output file, one per line
with open(output_filename, "w", encoding="utf-8") as outfile:
    for code in stock_codes:
        outfile.write(code + "\n")

print(f"Saved {len(stock_codes)} stock codes to '{output_filename}'.")
