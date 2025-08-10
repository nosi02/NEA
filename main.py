import csv
from datetime import datetime, date
from collections import OrderedDict
import matplotlib.pyplot as plt


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

# Calculate totals
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
        if qty_str == '':
            qty = 0
        else:
            qty = int(qty_str)

        # Store with date object as key for proper sorting
        temp_dict[item_date] = temp_dict.get(item_date, 0) + qty

# Create OrderedDict sorted by date
Sum_of_Qty_Sold = OrderedDict(sorted(temp_dict.items()))

#Read product-group file
with open('Data/Product Group.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    group_list = []
    for row in csv_reader:
        group_list.append(row)
#add product group to product dictionaries
for product in data_list:
    # go into product group
    for item in group_list:
        if item['Products'] == product['Description']:
            product['Group'] = item["Product groups"]
#total quantity sold in each group
group_dict = {}
for product in data_list:
    if "Group" in product:  # Check if key exists
        group_name = product["Group"]
        group_dict[group_name] = group_dict.get(group_name, 0) + 1

#calculate total sold each day of a partiulcar group
temp_dict = {}
for item in data_list:
    # Skip if no valid date
    if item['Parsed.Date'] is None:
        continue
    # Check if date is in range
    item_date = item['Parsed.Date'].date()
    if start <= item_date <= end:
        # Handle empty QTY values
        if "Group" in item and item["Group"] == "Allergy Relief":
            qty_str = item.get('QTY Sold', '').strip()
            if qty_str == '':
                qty = 0
            else:
                qty = int(qty_str)
            temp_dict[item_date] = temp_dict.get(item_date, 0) + qty
Sum_of_Grp_Qty_Sold = OrderedDict(sorted(temp_dict.items()))

temp_dict = {}
#creating sales each day for each group
for item in data_list:
    # Skip if no valid date
    if item['Parsed.Date'] is None:
        continue
    # Check if date is in range
    item_date = item['Parsed.Date'].date()
    if start <= item_date <= end:
         if "Group" in item and item["Group"] :
            qty_str = item.get('QTY Sold', '').strip()
            if qty_str == '':
                qty = 0
            else:
                qty = int(qty_str)
            # create group if not exists
            if item["Group"] not in temp_dict:
                    temp_dict[item["Group"]] = {}
            if item_date not in temp_dict[item["Group"]]:
                temp_dict[item["Group"]][item_date] = 0
            temp_dict[item["Group"]][item_date] += qty

# get into 2d lists
qty_per_group = {}
for group, date_dict in temp_dict.items():
   qty_per_group[group] = []
   sorted_dates = sorted(date_dict.items())
   for date, qty in sorted_dates:
       qty_per_group[group].append([date.strftime('%d/%m/%y'), qty])

print(qty_per_group)
# Store with date object as key for proper sorting
#Creates bar chart of product groups each day
#dates = list(Sum_of_Qty_Sold.keys())
#units = list(data_list["Group"].values())
#plt.bar(range(len(Sum_of_Qty_Sold)), units, tick_label=dates)
#plt.show()


#Creates bar chart of units each day
#dates = list(Sum_of_Qty_Sold.keys())
#units = list(Sum_of_Qty_Sold.values())
#plt.bar(range(len(Sum_of_Qty_Sold)), units, tick_label=dates)
#plt.show()

# Print how many units each day
#print("\n=== Sales by Date (Ordered) ===")
#for date_obj, total in Sum_of_Qty_Sold.items():
    #print(f"{date_obj.strftime('%d/%m/%y')}: {total} units")

#print(f"\nTotal: {sum(Sum_of_Qty_Sold.values())} units")

# ----------------------------------------------------------------------------------------
# OOP forcasting model - weighted moving average
#-----------------------------------------------------------------------------------------

class Forecaster:
    def __init__(self, product_name, sales_data ):
        self.product_des = product_name
        self.sales_data = sales_data
    def weight_moving_average(self,weight):
        weighted_sum = weight