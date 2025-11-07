import Database as db
from Forecaster import Forecaster
from MRP import MRP
import matplotlib.pyplot as plt
from datetime import datetime

# --- GET DATA FROM DATABASE ---
print("Loading data from database...")
all_group_names = db.get_all_group_names()
inventory_list = db.get_inventory_levels()
lead_times, safety_stocks = db.get_mrp_parameters()
sales_mix = db.get_sales_mix()
print("Data loaded successfully.")


# --- RUN FORECASTING & MRP ---
window_size = 7 #will make user defined
days_to_predict = 30  #will make user defined

print("--- Starting Main Process ---")
all_forecasts = {}

# --- MAIN FORECASTING LOOP ---
for grp_name in all_group_names:

    print(f"--- Checking Group: {grp_name} ---")

    # Get the sales data for this specific group from the DB
    sales_list = db.get_sales_data_by_group(grp_name)

    # Check if there is enough data
    if len(sales_list) <= window_size:
        print(f"Result: SKIPPED. Only {len(sales_list)} data points available.")
        print("-" * 35)
        all_forecasts[grp_name] = [0] * days_to_predict  # Add a 0 forecast for the MRP
        continue  # Move to the next group

    # If the code reaches here, the group has enough data
    print("Result: OK. Proceeding with forecast.")

    forecaster = Forecaster(grp_name, sales_list) #Create the Forecaster object
    future_predictions = forecaster.predict_future_sequence(days_to_predict, window_size) #generate forecast
    all_forecasts[grp_name] = future_predictions  # Store the list of predicted values

    # Generate accuracy and plot
    # accuracy = forecaster.calculate_accuracy()
    # all_historical_forecasts = forecaster.generate_all_forecasts(window_size)
    # forecaster.plot_forecast(window_size, all_historical_forecasts)

    print("-" * 35)

print("\n--- Forecasting Complete ---")

# --- RUN MRP PLANNER ---
print("\n--- Running Materials Requirement Plan ---")


mrp_engine = MRP(all_forecasts, inventory_list, lead_times, safety_stocks, sales_mix)
procurement_plan = mrp_engine.order_plan() # get final procurement plan

# ----- Display the results --------
print("\n--- Recommended Procurement Plan ---")
if procurement_plan:
    for order in procurement_plan:
        print(order)
else:
    print("No procurement orders needed at this time.")

print("\n--- Main Process Complete ---")