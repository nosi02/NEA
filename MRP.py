import csv
from Forecaster import Forecaster
from main import qty_per_group, data_list, group_list
from datetime import datetime, timedelta
with open('Data/Product Group.csv', mode='r') as file:
    reader = csv.DictReader(file)
    inventory_list = {}
    for product in reader:
        group_name = product['Product groups']
        inventory_value = int(product["QTY"])
        inventory_list[group_name] = inventory_list.get(group_name, 0) + inventory_value
default_lead_time = 3
default_safety_stock = 2
all_product_groups = list(qty_per_group.keys())
lead_times = {}
for group in all_product_groups:
    lead_times[group] = default_lead_time
# if I need to overwrite can just do lead_times['Skin Care'] = 14 or something
safety = {}
for group in all_product_groups:
    safety[group] = default_safety_stock

all_forecasts = {}
window_size = 7
days_to_predict = 7 # Plan 7 days into the future
for group_name, sales_data in qty_per_group.items():
    if len(sales_data) > window_size:
        forecaster = Forecaster(group_name, sales_data)
        future_forecast = forecaster.predict_future_sequence(days_to_predict, window_size)
        all_forecasts[group_name] = future_forecast

# calcualte total group sales
group_sales_totals = {}
for item in data_list:
    if "Group" in item:
        qty_str = item.get('QTY Sold', '').strip()
        if qty_str == '':
            qty = 0
        else:
            qty = int(qty_str)
        group_sales_totals[item["Group"]] = group_sales_totals.get(item["Group"], 0) + qty

#calculate total group sales
product_sales_totals = {}
for product in data_list:
    if "Group" in product:
        prd_name = product["Description"]
        if "Group" in product:
            qty_str = product.get('QTY Sold', '').strip()
            if qty_str == '':
                qty = 0
            else:
                qty = int(qty_str)
        product_sales_totals[prd_name] = product_sales_totals.get(prd_name, 0) + qty

sales_mix = {}
for row in group_list:
    product_name = row['Products']
    group_name = row['Product groups']
    product_total = product_sales_totals.get(product_name, 0)
    group_total = group_sales_totals.get(group_name, 0)
    if group_total == 0:
        percentage = 0
    else:
        percentage = product_total / group_total
    if group_name in sales_mix:
        sales_mix[group_name][product_name] = percentage
    else:
        sales_mix[group_name] = {}
        sales_mix[group_name][product_name] = percentage

class MRP:
    def __init__(self, lead_time, forecasts, inventory, safety_stocks, period, sales_mix):
        self.inventory = inventory
        self.lead_times = lead_time
        self.safety_stock = safety_stocks
        self.forecast_sales = forecasts
        self.period_length = period
        self.sales_mix = sales_mix
    def order_plan(self):
        planned_orders = []
        today = datetime.now()
        for grp_name, daily_forecasts in self.forecast_sales.items():
            # get specific details for each product group
            projected_inventory = self.inventory.get(grp_name, 0)
            lead_time = self.lead_times.get(grp_name, 0)
            safety_stock = self.safety_stock.get(grp_name, 0)
            period_time = self.period_length
            cooldown = -1 # no new orders until after this day
            # predict inventory day by day
            #enumerate makes it a tuple so can loop through it
            for day_index, demand in enumerate(daily_forecasts):
                projected_inventory -= demand
                if projected_inventory <= safety_stock and day_index >= cooldown:
                    deficit = safety_stock - projected_inventory
                    future_demand_slice = daily_forecasts[day_index: day_index + lead_time + period_time]
                    demand_during_lead_time = sum(future_demand_slice)
                    quantity_to_order = deficit + demand_during_lead_time

                    # Avoid placing tiny orders
                    if quantity_to_order <= 0:
                        continue

                    # figure out when order must be placed
                    order_placement_date = today + timedelta(days=day_index - lead_time)
                    expected_arrival_date = today + timedelta(days=day_index)

                    #create order list
                    product_mix = self.sales_mix[grp_name]
                    for product_name, percentage in product_mix.items():
                        individual_quantity = round(quantity_to_order * percentage)
                        if individual_quantity <= 0: # Avoid placing tiny orders
                            continue
                        individual_order_list = {
                            'Product': product_name,
                            'QuantityToOrder': individual_quantity,
                            'ProductGroup': grp_name,
                            'OrderPlacementDate': order_placement_date.strftime('%Y-%m-%d'),
                            'ExpectedArrivalDate': expected_arrival_date.strftime('%Y-%m-%d')
                         }
                        planned_orders.append(individual_order_list)

                    projected_inventory += quantity_to_order # inventory increase due to planned order
                    cooldown = day_index + period_time #not place another order until after period time over
        return planned_orders

# --- Run the MRP Planner ---

# 1. Create the planner instance, giving it all the prepared data
mrp_engine = MRP(lead_times, all_forecasts, inventory_list, safety)

# 2. Run the algorithm to get your final procurement plan
procurement_plan = mrp_engine.order_plan()

# 3. Display the results
print("\n--- Recommended Order List---")
for order in procurement_plan:
    print(order)