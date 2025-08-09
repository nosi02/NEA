import csv
from datetime import datetime, date
from collections import OrderedDict

# Read the CSV file
with open('Data/Sales daily data merged.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    data_list = []
    for row in csv_reader:
        data_list.append(row)

# Parse dates and clean data
for data in data_list:
    data['Source.Name'] = data['Source.Name'].strip()
    try:
        parsed_date = datetime.strptime(data['Source.Name'], "%d/%m/%y")
        data['Parsed.Date'] = parsed_date
    except:
        data['Parsed.Date'] = None

# Set date range
start = date(2025, 5, 1)
end = date(2025, 7, 17)

# Calculate totals - using regular dict first
temp_dict = {}

for item in data_list:
    # Skip if no valid date
    if item['Parsed.Date'] is None:
        continue

    # Check if date is in range
    item_date = item['Parsed.Date'].date()
    if start <= item_date <= end:
        # Handle empty QTY values
        qty_str = item.get('QTY Sold', '').strip()
        qty = 0 if qty_str == '' else int(qty_str)

        # Store with date object as key for proper sorting
        temp_dict[item_date] = temp_dict.get(item_date, 0) + qty

# Create OrderedDict sorted by date
Sum_of_Qty_Sold = OrderedDict(sorted(temp_dict.items()))

# Print results
print("\n=== Sales by Date (Ordered) ===")
for date_obj, total in Sum_of_Qty_Sold.items():
    print(f"{date_obj.strftime('%d/%m/%y')}: {total} units")

print(f"\nTotal: {sum(Sum_of_Qty_Sold.values())} units")