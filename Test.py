# test_data = [['01/05/25', 1], ['02/05/25', 2], ['08/05/25', 2], ['15/05/25', 2], ['27/05/25', 4], ['30/05/25', 12], ['02/06/25', 8], ['03/06/25', 4], ['04/06/25', 8]]
# weights = [1,2,3,4,5,6,7,8,9,10]
# weighted_sum =  sum(weights)
# forecast = 0
# for i in range(len(weights) -1) :
#     forecast = forecast + (test_data[i][1] * weights[i])
# forecast = forecast / weighted_sum
# print(forecast)
# real = ['11/06/25', 4]

# import Database as db
#
# print("--- 1. TESTING: get_all_group_names() ---")
# names = db.get_all_group_names()
# print(f"Found {len(names)} groups. First 5: {names[:5]}")
# print("-" * 20)
#
# print("--- 2. TESTING: get_inventory_levels() ---")
# inventory = db.get_inventory_levels()
# print(f"Found {len(inventory)} inventory records. e.g., Skin Care: {inventory.get('Skin Care')}")
# print("-" * 20)
#
# print("--- 3. TESTING: get_sales_data_by_group() ---")
# sales_data = db.get_sales_data_by_group('Skin Care') # Test with a group you know has data
# print(f"Found {len(sales_data)} sales records for Skin Care. First 5: {sales_data[:5]}")
# print("-" * 20)
#
# print("--- 4. TESTING: get_sales_mix() ---")
# sales_mix = db.get_sales_mix()
# print(f"Calculated sales mix. e.g., Skin Care mix: {sales_mix.get('Skin Care')}")
# print("-" * 20)

# import Database as db
# from Forecaster import Forecaster
#
# print("--- TESTING: Forecaster Class ---")
# # Get data for one good group
# sales_data = db.get_sales_data_by_group('Skin Care')  # Use a group with lots of data
#
# if sales_data and len(sales_data) > 7:
#     f = Forecaster('Skin Care', sales_data)
#
#     # Test future forecast
#     future = f.predict_future_sequence(num_days=5, window_size=7)
#     print(f"Future Forecast: {future}")
#
#     # Test accuracy
#     accuracy = f.calculate_accuracy(window_size=7)  # Assumes you've built this
#     print(f"Accuracy Metrics: {accuracy}")
#
#     # Test plotting
#     hist_forecast = f.generate_all_forecasts(window_size=7)
#     f.plot_forecast(window_size=7, forward=hist_forecast)
#     print("Plot generated. Check the plot window.")
# else:
#     print("Could not test Forecaster: Not enough sales data for 'Skin Care'.")

# import Database as db
# from MRP import MRP
#
# print("--- TESTING: MRP Class ---")
# # Get all the real data from the DB
# inventory = db.get_inventory_levels()
# lead_times, safety_stocks = db.get_mrp_parameters()
# sales_mix = db.get_sales_mix()
#
# # Create a DUMMY forecast to test the MRP logic
# dummy_forecasts = {
#     'Skin Care': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
#     'Pain Relief': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
# }
#
# mrp_engine = MRP(
#     lead_time=lead_times,
#     forecasts=dummy_forecasts, # Use the dummy data
#     inventory=inventory,
#     safety_stocks=safety_stocks,
#     period=7, # Your period length
#     sales_mix=sales_mix
# )
#
# plan = mrp_engine.order_plan()
# print("MRP Plan Generated:")
# for order in plan[:5]: # Print first 5 orders
#     print(order)