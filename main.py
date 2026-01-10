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

#------ will need to create login hear---------------------

       product_frame = ctk.CTkFrame(products_tab, width=200, height=200, corner_radius=10, bg_color="white")
        product_frame.pack(pady=10, padx=10, fill="x")

        Frame for the table
        product_table_frame = ctk.CTkFrame(products_tab)
       product_table_frame.pack(pady=10, padx=10, fill="both", expand=True)
       product_columns = ("Product Name", "Product Group")
        self.product_tree = ttk.Treeview(product_table_frame, columns=product_columns, show="headings")

        Create Table
        for col in product_columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=150)
        self.product_tree.pack(side="left", fill="both", expand=True)
        self.refresh_product_table()  # so tab is not empty

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(product_table_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Make a button
        self.add_product_button = ctk.CTkButton(product_frame, text="Add New Product", command=self.on_add_product_click)
        self.add_product_button.pack(side="left", padx=10)

        # Make a button
        self.delete_product_button = ctk.CTkButton(product_frame, text="Delete Selected Product", command=self.on_delete_product_click)
        self.delete_product_button.pack(side="left", padx=10)

        # Make a Widget for New Product
        self.new_product_name = ctk.CTkLabel(product_frame, text= "Product Name", font=("Arial", 12), fg_color="transparent")
        self.new_product_name.pack(side="left", padx=10)
        self.new_product_name_entry = ctk.CTkEntry(product_frame, placeholder_text="Enter Name of New Product")
        self.new_product_name_entry.pack(side="left", padx=10)

        # Make a Widget for New Product group
        self.new_product_grp = ctk.CTkLabel(product_frame, text="Product Group", font=("Arial", 12), fg_color="transparent")
        self.new_product_grp.pack(side="left", padx=10)
        self.grp_entry = ctk.CTkEntry(product_frame, placeholder_text="Enter Name of New Product's Group")
        self.grp_entry.pack(side="left", padx=10)

        self.suggestions_box = ctk.CTkTextbox(product_frame)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)