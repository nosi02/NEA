import customtkinter as ctk
import csv
import Database as db
from Forecaster import Forecaster
from MRP import MRP
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading
import traceback
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.all_group_names = db.get_all_group_names()
        self.inventory_list = db.get_inventory_levels()
        self.lead_times, self.safety_stocks = db.get_mrp_parameters()
        self.sales_mix = db.get_sales_mix()
        self.plot_canvas = None
        # Creating a Window
        self.title("Inventory Manager")
        self.geometry("1200x700")
        ctk.set_appearance_mode("system")

        #adding tabs
        tabview = ctk.CTkTabview(self, width=1150, height=650)
        tabview.pack(padx=20, pady=20)
        forecast_tab = tabview.add("Forecast & Analysis")
        mrp_tab = tabview.add("MRP Plan")
        settings_tab = tabview.add("Settings")
        products_tab = tabview.add("Product Management")

        # --- "Forecast & Analysis" Tab / "Main" Tab---

        # Create a 2-column layout
        forecast_tab.grid_columnconfigure(0, weight=1)  # Control panel column
        forecast_tab.grid_columnconfigure(1, weight=3)  # Chart column
        forecast_tab.grid_rowconfigure(0, weight=1)  # Full height for both

        #creating a frame
        self.main_frame = ctk.CTkFrame(forecast_tab,width=200,height=200,corner_radius=10,bg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # creating a label
        label = ctk.CTkLabel(self.main_frame, text="Forecasting Controls", font=ctk.CTkFont(size=16, weight="bold"))
        label.grid(padx=10, pady=12)

        #Creating a dropdown menu
        self.group_combobox = ctk.CTkComboBox(self.main_frame, values=db.get_all_group_names())
        self.group_combobox.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        #Make a button
        self.forecast_button = ctk.CTkButton(self.main_frame, text="Run Forecast & Analysis", command=self.on_run_forecast_click )
        self.forecast_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # Make a Widget for Days to predict
        self.days_to_predict = ctk.CTkLabel( self.main_frame, text="Days to Predict", font=("Arial", 12), fg_color="transparent")
        self.days_to_predict.grid(row=3, column=0, pady=(10,0), padx=10, sticky="w")
        self.days_entry = ctk.CTkEntry( self.main_frame, placeholder_text="Enter How many days ahead you want to predict")
        self.days_entry.grid(row=3, column=1, pady=(10,0), padx=10, sticky="ew")

        # Make a Widget for Window Size
        self.window_label = ctk.CTkLabel( self.main_frame, text="Window Size", font=("Arial", 12), fg_color="transparent")
        self.window_label.grid(row=2, column=0, pady=(10,0), padx=10, sticky="w")
        self.window_entry = ctk.CTkEntry( self.main_frame, placeholder_text="Enter Window Size")
        self.window_entry.grid(row=2, column=1, pady=(10,0), padx=10, sticky="ew")

        #Make a label for Accuracy
        self.accuracy_label = ctk.CTkLabel(self.main_frame, text= "Accuracy (MAE): N/A | (RMSE): N/A", font=("Arial", 12), fg_color="transparent")
        self.accuracy_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        #Make Alert Panel
        self.alert_panel = ctk.CTkTextbox(forecast_tab)
        self.alert_panel.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.alert_panel.tag_config("critical", foreground="red")
        self.alert_panel.tag_config("warning", foreground="orange")
        for group_name in self.all_group_names:
            inventory_qty = self.inventory_list.get(group_name, 0)
            safety_qty = self.safety_stocks.get(group_name, 0)
            if inventory_qty <= 0:
                message = f"CRITICAL: Out of stock of {group_name}!\n"
                self.alert_panel.insert("end", message, "critical")
            elif inventory_qty <= safety_qty:
                message = f"WARNING: Low stock for {group_name}!\n"
                self.alert_panel.insert("end", message, "warning")

        #Place for Top 5 seller analytics
        self.top_sellers_box = ctk.CTkTextbox(forecast_tab)
        self.top_sellers_box.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        top_5 = db.get_top_selling_products()
        bottom_5 = db.get_bottom_selling_products()
        for product,amount in top_5:
            self.top_sellers_box.insert("end", f"TOP 5 Products: {product} where {amount} were sold!\n")
        for product,amount in bottom_5:
            self.top_sellers_box.insert("end", f"BOTTOM 5 Products: {product} where {amount} were sold!\n")


        #Empty Frame where I will add a matplotlib chart
        self.chart_frame = ctk.CTkFrame(forecast_tab, width=200, height=200, corner_radius=10, bg_color="transparent")
        self.chart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        #Second Chart for weekly sales
        self.weekly_chart_frame = ctk.CTkFrame(forecast_tab)
        self.weekly_chart_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        weekday_labels, sales_totals = db.get_sales_for_last_n_days()
        if sales_totals:  # Only plot if we have data
            #Create a NEW Figure object
            fig2 = Figure(figsize=(6, 3), dpi=100)
            ax2 = fig2.add_subplot(111)
            # Create the bar chart
            ax2.bar(weekday_labels, sales_totals, color='cornflowerblue')
            ax2.set_title("Sales This Week")
            ax2.set_ylabel("Quantity Sold")
            # Embed figure into its frame
            canvas2 = FigureCanvasTkAgg(fig2, master=self.weekly_chart_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="top", fill="both", expand=True)

        #--- "MRP Plan" Tab ---------------

        # creating a frame for mrp tab
        self.mrp_frame = ctk.CTkFrame(mrp_tab, width=200, height=200, corner_radius=10, bg_color="white")
        self.mrp_frame.pack(pady=10, padx=10, fill="x")

        #progress bar
        self.mrp_progress = ctk.CTkProgressBar(self.mrp_frame, mode="indeterminate")
        self.mrp_progress.pack(fill="x", padx=10, pady=5)
        self.mrp_progress.pack_forget()

        # Make a button
        self.mrp_button = ctk.CTkButton(self.mrp_frame, text="Generate Procurement Plan", command=self.on_run_mrp_click)
        self.mrp_button.pack(side="left", padx=10, pady=10)

        # Make a button
        self.export_button = ctk.CTkButton(self.mrp_frame, text="Export Plan to CSV", command=self.on_export_click)
        self.export_button.pack(side="left", padx=10, pady=10)

        # Create a new frame just for the entry widgets
        entry_frame = ctk.CTkFrame(self.mrp_frame, fg_color="transparent")
        entry_frame.pack(side="left", fill="x", expand=True, padx=10)
        self.mrp_window_label = ctk.CTkLabel(entry_frame, text="Window Size:", font=("Arial", 12))
        self.mrp_window_label.pack(side="left")
        self.mrp_window_entry = ctk.CTkEntry(entry_frame, placeholder_text="e.g., 7")
        self.mrp_window_entry.pack(side="left", padx=5)

        self.mrp_days_label = ctk.CTkLabel(entry_frame, text="Days to Predict:", font=("Arial", 12))
        self.mrp_days_label.pack(side="left", padx=(10, 0))
        self.mrp_days_entry = ctk.CTkEntry(entry_frame, placeholder_text="e.g., 30")
        self.mrp_days_entry.pack(side="left", padx=5)

        #Frame for the table
        mrp_table_frame = ctk.CTkFrame(mrp_tab)
        mrp_table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        mrp_columns = ("Product", "Product Group", "Quantity", "Order Date", "Arrival Date")
        self.mrp_tree = ttk.Treeview(mrp_table_frame, columns=mrp_columns, show="headings")

        #Create Table
        for col in mrp_columns:
            self.mrp_tree.heading(col, text=col)
            self.mrp_tree.column(col, width=150)

        self.mrp_tree.pack(side="left", fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(mrp_table_frame, orient="vertical", command=self.mrp_tree.yview)
        self.mrp_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- "Settings" Tab ---

        # creating a frame for setting tab
        self.setting_frame = ctk.CTkFrame(settings_tab)
        self.setting_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.save_settings_button = ctk.CTkButton(self.setting_frame , text="Save Changes", command=self.save_changes)
        self.save_settings_button.pack(pady=10)

        # Make a Widget for Lead Time and Safety Stock
        self.edit_lead_time = ctk.CTkEntry(self.setting_frame, placeholder_text="Enter Lead Time")
        self.edit_lead_time.pack(pady=5)
        self.edit_safety_stock = ctk.CTkEntry(self.setting_frame, placeholder_text="Enter Safety Stock")
        self.edit_safety_stock.pack(pady=5)
        self.edit_group_label = ctk.CTkLabel(self.setting_frame, text="Select a group to edit")
        self.edit_group_label.pack(pady=5)

        # Create the Treeview for settings
        settings_columns = ("Product Group", "Lead Time (Days)", "Safety Stock (Units)")
        self.settings_tree = ttk.Treeview(self.setting_frame, columns=settings_columns, show="headings")
        self.settings_tree.pack(fill="both", expand=True)

        self.settings_tree.bind("<<TreeviewSelect>>", self.on_settings_row_select)
        self.setting_frame.bind("<<TreeviewSelect>>", self.on_settings_row_select)


        for col in settings_columns:
            self.settings_tree.heading(col, text=col)
            self.settings_tree.column(col, width=200)

        self.settings_tree.pack(fill="both", expand=True)
        for group_name in self.all_group_names:
            lead = self.lead_times.get(group_name, 3)
            stock = self.safety_stocks.get(group_name, 2)
            #Column order
            row_data = (group_name, lead,stock )
            # Insert the new row
            self.settings_tree.insert("", "end", values=row_data)

        # --- "Product Management" Tab ---
        product_frame = ctk.CTkFrame(products_tab, width=200, height=200, corner_radius=10, bg_color="white")
        product_frame.pack(pady=10, padx=10, fill="x")

        # Frame for the table
        product_table_frame = ctk.CTkFrame(products_tab)
        product_table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        product_columns = ("Product Name", "Product Group")
        self.product_tree = ttk.Treeview(product_table_frame, columns=product_columns, show="headings")

        # Create Table
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

        #------------- Logging Console ---------
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(padx=20, pady=(0, 20), fill="x", side="bottom")



    def on_run_forecast_click(self):
        if self.plot_canvas: #clean up old plot
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None  #
        # message for when run forcast clicked
        self.log("Running forecast...")
        grp_name = self.group_combobox.get()
        #Error checking
        if not grp_name:
            self.log("No group selected")
            return
        window_size = int(self.window_entry.get()) # will need to do error handling
        sales_data = db.get_sales_data_by_group(grp_name)
        f = Forecaster(grp_name,sales_data)
        #Updating accuracy label on GUI
        accuracy = f.calculate_accuracy(window_size)
        mae = accuracy.get('MAE', 0)
        rmse = accuracy.get('RMSE', 0)
        new_text = f"Accuracy (MAE): {mae:.2f} | (RMSE): {rmse:.2f}"
        self.accuracy_label.configure(text=new_text)

        hist_forecast = f.generate_all_forecasts(window_size)
        fig = f.plot_forecast(window_size,forward=hist_forecast)
        # creating new plot
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.plot_canvas = canvas


    def on_run_mrp_click(self):
        window_size = int(self.mrp_window_entry.get())  # have to do error handling
        days_to_predict = int(self.mrp_days_entry.get())
        #Show the progress bar
        self.mrp_progress.pack(side="top", fill="x", padx=10, pady=5)
        self.mrp_progress.start()
        # message for when run mrp clicked
        self.log("Running MRP, please wait...")
        #disable button
        self.mrp_button.configure(state="disabled", text="Running...")
        #split function as GUI was freezing
        thread = threading.Thread(target=self._run_mrp_logic_in_thread,
                                  args=(window_size, days_to_predict))
        thread.start()
    def _run_mrp_logic_in_thread(self, window_size, days_to_predict):
        all_forecasts = {}
        for grp_name in self.all_group_names:
            sales_list = db.get_sales_data_by_group(grp_name)
            # Check if there is enough data
            if len(sales_list) <= window_size:
                self.after(0,self.log,f"Result: SKIPPED. Only {len(sales_list)} data points available.")
                self.after(0,self.log,"-" * 35)
                all_forecasts[grp_name] = [0] * days_to_predict  # Add a 0 forecast for the MRP
                continue  # Move to the next group
            forecaster = Forecaster(grp_name, sales_list)
            future_predictions = forecaster.predict_future_sequence(days_to_predict, window_size)
            all_forecasts[grp_name] = future_predictions
        # need to look at what period should be based on
        mrp_plan = MRP(all_forecasts, self.inventory_list, self.lead_times, self.safety_stocks,days_to_predict, self.sales_mix)
        procurement_plan = mrp_plan.order_plan()
        self.current_plan = procurement_plan
        #Schedule the GUI update back on the main thread
        self.after(0, self._populate_mrp_table, procurement_plan)

    def _populate_mrp_table(self, procurement_plan):
        all_items = self.mrp_tree.get_children()
        self.mrp_tree.delete(*all_items)
        for order in procurement_plan:
            #Column order
            row_data = (
                order['Product'],
                order['ProductGroup'],
                order['QuantityToOrder'],
                order['OrderPlacementDate'],
                order['ExpectedArrivalDate']
            )
            # Insert the new row
            self.mrp_tree.insert("", "end", values=row_data)
        self.log("MRP run complete.")
        self.mrp_progress.stop()
        self.mrp_progress.pack_forget()
        self.mrp_button.configure(state="normal", text="Generate Procurement Plan")


    def on_export_click(self):
        # message for when run export clicked
        self.log("Exporting plan...")
        csv_file = "order_plan.csv"
        if len(self.current_plan) != 0:
            headers = self.current_plan[0].keys()
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.current_plan)

    def refresh_settings_table(self):
        # Clear the table
        self.settings_tree.delete(*self.settings_tree.get_children())
        # Reload the data from the DB
        self.lead_times, self.safety_stocks = db.get_mrp_parameters()
        # Repopulate
        for group_name in self.all_group_names:
            row_data = (group_name, self.lead_times[group_name], self.safety_stocks[group_name])
            self.settings_tree.insert("", "end", values=row_data)

    def save_changes(self):
        self.log("Saving settings to database...")
        group_name = self.edit_group_label.cget("text")
        new_lead_time = int(self.edit_lead_time.get())
        new_safety_stock = int(self.edit_safety_stock.get())
        db.update_mrp_parameters(group_name, new_lead_time, new_safety_stock)
        self.refresh_settings_table()

    def refresh_product_table(self):
        # Clear the table
        self.product_tree.delete(*self.product_tree.get_children())
        all_products = db.get_all_products()
        # Repopulate
        for product in all_products:
            self.product_tree.insert("", "end", values=product)

    def on_add_product_click(self):
        name  = self.new_product_name_entry.get()
        group_name  = self.grp_entry.get()
        if not name or not group_name:
            self.log("Error: Name and group are required.")
            return
        message = db.add_new_product(name, group_name)
        self.log(message)
        # Refresh the table
        self.refresh_product_table()

    def on_delete_product_click(self):
        selected_item = self.product_tree.focus()
        if not selected_item:
            self.log("Error: No product selected.")
            return
        row_values = self.product_tree.item(selected_item, 'values')
        product_name = row_values[0]
        message = db.delete_product(product_name)
        self.log(message)
        # Refresh the table
        self.refresh_product_table()

    def on_settings_row_select(self, event):
        # Get the item the user clicked
        selected_item = self.settings_tree.focus()
        if not selected_item:
            return
        #  Get the values from that row
        row_values = self.settings_tree.item(selected_item, 'values')
        group_name, lead_time, safety_stock = row_values
        # First, clear entry boxes
        self.edit_group_label.configure(text=group_name)
        self.edit_lead_time.delete(0, "end")
        self.edit_safety_stock.delete(0, "end")
        # Then, insert the new values
        self.edit_lead_time.insert(0, lead_time)
        self.edit_safety_stock.insert(0, safety_stock)

    def log(self, message):
        # Adds a message to the logging console
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")  # Auto-scroll to the bottom


# --- Add these lines at the end ---
if __name__ == "__main__":
    app = App()
    app.mainloop()

#add a box that will show errors etc