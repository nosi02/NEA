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
from tkinter import messagebox


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            db.create_connection() #testing the connection
        except Exception as e:
            #show popup so inform user
            messagebox.showerror("Fatal Error", f"Could not load database.\n\nReason: {e}")
            self.destroy()#destoy app
            return
        self.all_group_names = db.get_all_group_names()
        self.inventory_list = db.get_inventory_levels()
        self.lead_times, self.safety_stocks = db.get_mrp_parameters()
        self.sales_mix = db.get_sales_mix()
        self.product_costs = db.get_product_costs()
        self.plot_canvas = None
        # Creating a Window
        self.title("Inventory Manager")
        self.geometry("1300x850")
        ctk.set_appearance_mode("system")

        # ------------- Logging Console ---------
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(padx=20, pady=(0, 20), fill="x", side="bottom")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #adding tabs
        tabview = ctk.CTkTabview(self, width=1150, height=650)
        tabview.pack(padx=20, pady=(10,5), fill="both", expand=True)
        forecast_tab = tabview.add("Forecast & Analysis")
        mrp_tab = tabview.add("MRP Plan")
        settings_tab = tabview.add("Settings")
        products_tab = tabview.add("Product Management")

        # --- "Forecast & Analysis" Tab / "Main" Tab---

        # Create a 2-column layout
        forecast_tab.grid_columnconfigure(0, weight=1)  # Control panel column
        forecast_tab.grid_columnconfigure(1, weight=3)  # Chart column
        forecast_tab.grid_rowconfigure(0, weight=2) # Full height for both
        forecast_tab.grid_rowconfigure(1, weight=1)#weekly chart

        #creating a frame
        self.main_frame = ctk.CTkFrame(forecast_tab)
        self.main_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        # creating a label
        ctk.CTkLabel(self.main_frame, text="Forecasting Controls", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        #Creating a dropdown menu
        ctk.CTkLabel(self.main_frame, text="Product Group:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.group_combobox = ctk.CTkComboBox(self.main_frame, values=db.get_all_group_names())
        self.group_combobox.grid(row=1, column=1, pady=5, padx=10, sticky="ew")

        #Make a button
        self.forecast_button = ctk.CTkButton(self.main_frame, text="Run Forecast & Analysis", command=self.on_run_forecast_click )
        self.forecast_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # Make a Widget for Days to predict
        self.days_to_predict = ctk.CTkLabel( self.main_frame, text="Days to Predict", font=("Arial", 12), fg_color="transparent")
        self.days_to_predict.grid(row=3, column=0, pady=5, padx=10, sticky="w")
        self.days_entry = ctk.CTkEntry( self.main_frame, placeholder_text="Enter How many days ahead you want to predict")
        self.days_entry.grid(row=3, column=1, pady=5, padx=10, sticky="ew")

        # Make a Widget for Window Size
        self.window_label = ctk.CTkLabel( self.main_frame, text="Window Size", font=("Arial", 12), fg_color="transparent").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.window_entry = ctk.CTkEntry( self.main_frame, placeholder_text="Enter Window Size")
        self.window_entry.grid(row=2, column=1, pady=5, padx=10, sticky="ew")

        #Make a label for Accuracy
        self.accuracy_label = ctk.CTkLabel(self.main_frame, text= "Accuracy (MAE): N/A | (RMSE): N/A", font=("Arial", 12), fg_color="transparent")
        self.accuracy_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Make a button
        self.refresh_button = ctk.CTkButton(self.main_frame, text="Refresh All Data", command=self.refresh_all_data)
        self.refresh_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.all_forecast_button = ctk.CTkButton(self.main_frame, text="Forecast for All", fg_color="#2c3e50",command=self.on_run_all_forecast)
        self.all_forecast_button.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # 4. Status Panels (Bottom)
        status_container = ctk.CTkFrame(self)
        status_container.pack(side="bottom", fill="x", padx=20, pady=10)

        #Make Alert Panel
        self.alert_panel = ctk.CTkTextbox(status_container, height=80, width=400)
        self.alert_panel.pack(side="left", padx=5, fill="both", expand=True)
        self.alert_panel.tag_config("critical", foreground="red")
        self.alert_panel.tag_config("warning", foreground="orange")
        for group_name in self.all_group_names:
            clean_name = group_name.strip()
            inventory_qty = self.inventory_list.get(clean_name, 0)
            safety_qty = self.safety_stocks.get(clean_name, 0)
            if inventory_qty <= 0:
                message = f"CRITICAL: Out of stock of {clean_name}!\n"
                self.alert_panel.insert("end", message, "critical")
            elif inventory_qty <= safety_qty:
                message = f"WARNING: Low stock for {clean_name}!\n"
                self.alert_panel.insert("end", message, "warning")

        #Place for Top 5 seller analytics
        self.top_sellers_box = ctk.CTkTextbox(status_container, height=80, width=400)
        self.top_sellers_box.pack(side="left", padx=5, fill="both", expand=True)
        top_5 = db.get_top_selling_products()
        bottom_5 = db.get_bottom_selling_products()
        for product,amount in top_5:
            self.top_sellers_box.insert("end", f"TOP 5 Products: {product} where {amount} were sold!\n")
        for product,amount in bottom_5:
            self.top_sellers_box.insert("end", f"BOTTOM 5 Products: {product} where {amount} were sold!\n")


        #Empty Frame where I will add a matplotlib chart
        self.chart_frame = ctk.CTkFrame(forecast_tab)
        self.chart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        #Second Chart for weekly sales
        self.weekly_chart_frame = ctk.CTkFrame(forecast_tab)
        self.weekly_chart_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        #--- "MRP Plan" Tab ---------------

        # creating a frame for mrp tab
        self.mrp_frame = ctk.CTkFrame(mrp_tab)
        self.mrp_frame.pack(pady=10, padx=10, fill="x")

        #progress bar
        self.mrp_progress = ctk.CTkProgressBar(mrp_tab)
        self.mrp_progress.pack(fill="x", padx=20, pady=5)
        self.mrp_progress.pack_forget()

        # Make a button
        self.mrp_button = ctk.CTkButton(self.mrp_frame, text="Generate Procurement Plan", command=self.on_run_mrp_click)
        self.mrp_button.pack(side="left", padx=10)

        # Make a button
        self.export_button = ctk.CTkButton(self.mrp_frame, text="Export Plan to CSV", command=self.on_export_click)
        self.export_button.pack(side="left", padx=10)

        # Create a new frame just for the entry widgets
        #entry_frame = ctk.CTkFrame(self.mrp_frame, fg_color="transparent")
        #entry_frame.pack(side="left", fill="x", expand=True, padx=10)
        self.mrp_window_label = ctk.CTkLabel(self.mrp_frame, text="Window Size:").pack(side="left", padx=5)
        self.mrp_window_entry = ctk.CTkEntry(self.mrp_frame, placeholder_text="e.g., 7",width=60)
        self.mrp_window_entry.pack(side="left", padx=5)
        self.mrp_window_entry.insert(0, "7")

        self.mrp_days_label = ctk.CTkLabel(self.mrp_frame, text="Days to Predict:", font=("Arial", 12))
        self.mrp_days_label.pack(side="left", padx=5)
        self.mrp_days_entry = ctk.CTkEntry(self.mrp_frame, placeholder_text="e.g., 30",width=60)
        self.mrp_days_entry.pack(side="left", padx=5)
        self.mrp_days_entry.insert(0, "30")

        #Frame for the table
        mrp_table_frame = ctk.CTkFrame(mrp_tab)
        mrp_table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        mrp_columns = ("Product", "Quantity", "Product Group", "Supplier", "Unit Cost", "Total Cost", "Order Date", "Arrival Date")
        self.mrp_tree = ttk.Treeview(mrp_table_frame, columns=mrp_columns, show="headings")

        #Create Table
        for col in mrp_columns:
            self.mrp_tree.heading(col, text=col)
            self.mrp_tree.column(col, width=100)

        self.mrp_tree.pack(side="left", fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(mrp_table_frame, orient="vertical", command=self.mrp_tree.yview)
        self.mrp_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- "Settings" Tab ---

        # creating a frame for setting tab
        self.setting_frame = ctk.CTkFrame(settings_tab)
        self.setting_frame.pack(pady=10, padx=10, fill="both", expand=True)

        edit_pane = ctk.CTkFrame(self.setting_frame, width=250)
        edit_pane.pack(side="left", fill="y", padx=10, pady=10)

        self.save_settings_button = ctk.CTkButton(edit_pane , text="Save Changes", command=self.save_changes)
        self.save_settings_button.pack(pady=20,padx =10, fill="x")

        # Make a Widget for Lead Time and Safety Stock
        self.edit_lead_time = ctk.CTkEntry(edit_pane, placeholder_text="Enter Lead Time")
        self.edit_lead_time.pack(pady=5, padx=10, fill="x")
        self.edit_safety_stock = ctk.CTkEntry(edit_pane, placeholder_text="Enter Safety Stock")
        self.edit_safety_stock.pack(pady=5,padx=10, fill="x")
        self.edit_group_label = ctk.CTkLabel(edit_pane, text="Select a group to edit",font=("Arial", 12, "bold"))
        self.edit_group_label.pack(pady=10)

        set_table_pane = ctk.CTkFrame(self.setting_frame)
        set_table_pane.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create the Treeview for settings
        settings_columns = ("Product Group", "Lead Time (Days)", "Safety Stock (Units)")
        self.settings_tree = ttk.Treeview(set_table_pane, columns=settings_columns, show="headings")
        self.settings_tree.pack(fill="both", expand=True)
        for col in settings_columns:
            self.settings_tree.heading(col, text=col)
            self.settings_tree.column(col, width=200)

        self.settings_tree.bind("<<TreeviewSelect>>", self.on_settings_row_select)
        self.setting_frame.bind("<<TreeviewSelect>>", self.on_settings_row_select)

        self.settings_tree.pack(fill="both", expand=True)
        self.settings_tree.bind("<<TreeviewSelect>>", self.on_settings_row_select)
        for group_name in self.all_group_names:
            lead = self.lead_times.get(group_name, 3)
            stock = self.safety_stocks.get(group_name, 2)
            #Column order
            row_data = (group_name, lead,stock )
            # Insert the new row
            self.settings_tree.insert("", "end", values=row_data)

        # --- "Product Management" Tab ---
        product_frame = ctk.CTkFrame(products_tab)
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
        self.add_product_button = ctk.CTkButton(product_frame, text="Add New Product", command=self.on_add_product_click,width=60)
        self.add_product_button.pack(side="left", padx=10)

        # Make a button
        self.delete_product_button = ctk.CTkButton(product_frame, text="Delete Selected Product", command=self.on_delete_product_click,width=60)
        self.delete_product_button.pack(side="left", padx=10)

        prod_table_frame = ctk.CTkFrame(products_tab)
        prod_table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Make a Widget for New Product
        self.new_product_name = ctk.CTkLabel(product_frame, text= "Product Name", font=("Arial", 12), fg_color="transparent")
        self.new_product_name.pack(side="left", padx=10)
        self.new_product_name_entry = ctk.CTkEntry(product_frame, placeholder_text="Enter Name of New Product")
        self.new_product_name_entry.pack(side="left", padx=5)

        # Make a Widget for New Product group
        self.new_product_grp = ctk.CTkLabel(product_frame, text="Product Group", font=("Arial", 12), fg_color="transparent")
        self.new_product_grp.pack(side="left", padx=10)
        self.grp_entry = ctk.CTkEntry(product_frame, placeholder_text="Enter Name of New Product's Group")
        self.grp_entry.pack(side="left", padx=5)

        self.suggestions_box = ctk.CTkTextbox(product_frame, height=100)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        # Inside your tab setup
        sales_mgmt_frame = ctk.CTkFrame(products_tab)
        sales_mgmt_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(sales_mgmt_frame, text="Manual Sale Entry/Adjustment", font=("Arial", 14, "bold")).grid(row=0,
                                                                                                             column=0,
                                                                                                             columnspan=3,
                                                                                                             pady=5)

        # 1. Select Product (ComboBox)
        self.sale_product_select = ctk.CTkComboBox(sales_mgmt_frame, values=self.all_group_names, width=200)
        self.sale_product_select.grid(row=1, column=0, padx=5, pady=5)

        # 2. Quantity
        self.sale_qty_entry = ctk.CTkEntry(sales_mgmt_frame, placeholder_text="Qty", width=60)
        self.sale_qty_entry.grid(row=1, column=1, padx=5, pady=5)

        # 3. Date (Defaults to Today)
        self.sale_date_entry = ctk.CTkEntry(sales_mgmt_frame, width=120)
        self.sale_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sale_date_entry.grid(row=1, column=2, padx=5, pady=5)

        # 4. Action Button
        self.save_sale_button = ctk.CTkButton(sales_mgmt_frame, text="Save Sale Record",
                                              command=self.on_save_manual_sale)
        self.save_sale_button.grid(row=1, column=3, padx=5, pady=5)

        # 5. Bulk CSV Button
        self.bulk_upload_button = ctk.CTkButton(sales_mgmt_frame, text="Bulk Import CSV", fg_color="green",
                                                command=self.on_bulk_csv_import)
        self.bulk_upload_button.grid(row=1, column=4, padx=5, pady=5)

        # Initial Load
        self.refresh_all_data()



    def on_run_forecast_click(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
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
        try:
            window_size = int(self.window_entry.get())
        except ValueError:
            self.log("Error: Window size must be a number.")
            return
        try:
            num_days = int(self.days_entry.get())
        except ValueError:
            self.log("Error: Days to Predict size must be a number.")
            return
        sales_data = db.get_sales_data_by_group(grp_name)
        if len(sales_data) < window_size:
            self.log(f"Error: Not enough data for group '{grp_name}'.")
            return
        f = Forecaster(grp_name,sales_data)
        #Updating accuracy label on GUI
        accuracy = f.calculate_accuracy(window_size)
        mae = accuracy.get('MAE', 0)
        rmse = accuracy.get('RMSE', 0)
        new_text = f"Accuracy (MAE): {mae:.2f} | (RMSE): {rmse:.2f}"
        self.accuracy_label.configure(text=new_text)

        future_data = f.predict_future_sequence(num_days, window_size)
        fig = f.plot_forecast(window_size, forward=future_data)
        # creating new plot
        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.plot_canvas.draw()
        chart_widget = self.plot_canvas.get_tk_widget()
        chart_widget.pack(side="top", fill="both", expand=True)
        self.log(f"Forecast for {grp_name} updated successfully.")


    def on_run_mrp_click(self):
        try:
            window_size = int(self.mrp_window_entry.get())
        except ValueError:
            self.log("Error: Window size must be a number.")
            return  # have to do error handling
        try:
            days_to_predict = int(self.mrp_days_entry.get())
        except ValueError:
            self.log("Error: Days to Predict size must be a number.")
            return  # have to do error handling
        #Show the progress bar
        self.mrp_progress.pack(fill="x", pady=5)
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
            else:
                forecaster = Forecaster(grp_name, sales_list)
                future_predictions = forecaster.predict_future_sequence(days_to_predict, window_size)
                all_forecasts[grp_name] = future_predictions  # Move to the next group
        # need to look at what period should be based on
        mrp_plan = MRP(all_forecasts, self.inventory_list, self.lead_times, self.safety_stocks,days_to_predict, self.sales_mix,self.product_costs)
        procurement_plan = mrp_plan.order_plan()
        self.current_plan = procurement_plan
        #Schedule the GUI update back on the main thread
        self.after(0, self._populate_mrp_table, procurement_plan)

    def _populate_mrp_table(self, procurement_plan):
        all_items = self.mrp_tree.get_children()
        self.mrp_tree.delete(*all_items)
        if not procurement_plan:
            self.log("MRP: No orders required for the forecast period.")
        for order in procurement_plan:
            #Column order
            row_data = (
                order['Product'],
                order['QuantityToOrder'],
                order['ProductGroup'],
                order['Supplier'],
                f"£{order['UnitCost']:.2f}",
                f"£{order['TotalCost']:.2f}",
                order['OrderPlacementDate'],
                order['ExpectedArrivalDate']
            )
            # Insert the new row
            self.mrp_tree.insert("", "end", values=row_data)
        self.log("MRP run complete.")
        self.mrp_progress.stop()
        self.mrp_progress.pack_forget()
        self.mrp_button.configure(state="normal", text="Generate Procurement Plan")
        self.export_button.configure(state="normal" if procurement_plan else "disabled")


    def on_export_click(self):
        if not self.current_plan: return
        # message for when run export clicked
        self.log("Exporting plan...")
        csv_file = "order_plan.csv"
        if len(self.current_plan) != 0:
            headers = self.current_plan[0].keys()
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.current_plan)
        self.log(f"Plan exported to {csv_file}")

    def refresh_settings_table(self):
        # Clear the table
        self.settings_tree.delete(*self.settings_tree.get_children())
        # Reload the data from the DB
        self.lead_times, self.safety_stocks = db.get_mrp_parameters()
        # Repopulate
        for group_name in self.all_group_names:
            row_data = (group_name, self.lead_times[group_name], self.safety_stocks[group_name])
            self.settings_tree.insert("", "end", values=row_data)

    def update_weekly_chart(self):
        """Fetches sales data and redraws the weekly bar chart."""
        if not self.winfo_exists(): return
        if hasattr(self, 'weekly_canvas') and self.weekly_canvas:
            self.weekly_canvas.get_tk_widget().destroy()
        weekday_labels, sales_totals = db.get_sales_for_last_n_days()
        fig2 = Figure(figsize=(5, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        # Draw the bars
        ax2.bar(weekday_labels, sales_totals, color='cornflowerblue')
        ax2.set_title("Sales Volume This Week", fontsize=10, fontweight='bold')
        ax2.set_ylabel("Units Sold")
        # Adjust layout so labels don't get cut off
        fig2.tight_layout()
        # Place it in the GUI frame
        self.weekly_canvas = FigureCanvasTkAgg(fig2, master=self.weekly_chart_frame)
        self.weekly_canvas.draw()
        self.weekly_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def save_changes(self):
        self.log("Saving settings to database...")
        group_name = self.edit_group_label.cget("text")
        try:
            new_lead_time = int(self.edit_lead_time.get())
        except ValueError:
            self.log("Error: Lead time must be a number.")
            return
        try:
            new_safety_stock = int(self.edit_safety_stock.get())
        except ValueError:
            self.log("Error: Safety Stock must be a number.")
            return
        db.update_mrp_parameters(group_name, new_lead_time, new_safety_stock)
        self.refresh_settings_table()

    def refresh_product_table(self):
        # Clear the table
        # Clear existing rows to prevent duplication
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        try:
            all_products = db.get_all_products()
            for product in all_products:
                # Ensure we only insert if product has data
                if product:
                    self.product_tree.insert("", "end", values=product)
        except Exception as e:
            self.log(f"Error refreshing products: {e}")

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

    def on_product_select(self, event=None):
        selected_item = self.product_tree.focus()
        if not selected_item:
            return
        row_values = self.product_tree.item(selected_item, 'values')
        if not row_values:
            return
        product_name = row_values[0]
        new_list = db.get_product_suggestions(product_name)
        self.suggestions_box.delete("1.0", "end")#clear textbox
        if new_list:#insert suggestion
            self.suggestions_box.insert("1.0", f"Suggestions for {product_name}:\n")
            for item in new_list:
                self.suggestions_box.insert("end", f"- {item}\n")
        else:
            self.suggestions_box.insert("1.0", f"No linked products found for {product_name}.")

    def refresh_all_data(self):
        self.log("Refreshing system data...")
        self.all_group_names = db.get_all_group_names()
        self.inventory_list = db.get_inventory_levels()
        self.lead_times, self.safety_stocks = db.get_mrp_parameters()
        self.sales_mix = db.get_sales_mix()
        self.product_costs = db.get_product_costs()
        self.group_combobox.configure(values=self.all_group_names)
        self.refresh_settings_table()
        self.refresh_product_table()
        self.update_weekly_chart()
        #Clear and Repopulate Top Sellers Box
        self.top_sellers_box.delete("1.0", "end")
        top_5 = db.get_top_selling_products()
        bottom_5 = db.get_bottom_selling_products()
        self.top_sellers_box.insert("end", "--- TOP 5 PRODUCTS ---\n")
        for product, amount in top_5:
            self.top_sellers_box.insert("end", f"★ {product}: {amount} sold\n")
        self.top_sellers_box.insert("end", "\n--- BOTTOM 5 PRODUCTS ---\n")
        for product, amount in bottom_5:
            self.top_sellers_box.insert("end", f"⚠ {product}: {amount} sold\n")
        #Clear and Repopulate Alert Panel
        self.alert_panel.delete("1.0", "end")
        for group_name in self.all_group_names:
            clean_name = group_name.strip()
            inventory_qty = self.inventory_list.get(clean_name, 0)
            safety_qty = self.safety_stocks.get(clean_name, 0)
            if inventory_qty <= 0:
                self.alert_panel.insert("end", f"CRITICAL: {clean_name} is OUT OF STOCK!\n", "critical")
            elif inventory_qty <= safety_qty:
                self.alert_panel.insert("end", f"WARNING: {clean_name} is low ({inventory_qty})\n", "warning")

        self.log("All dashboard data has been refreshed.")
    def on_run_all_forecast(self):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        try:
            window_size = int(self.window_entry.get())
        except ValueError:
            self.log("Error: Window size must be a number.")
            return  # have to do error handling
        try:
            num_days = int(self.days_entry.get())
        except ValueError:
            self.log("Error: Days to Predict size must be a number.")
            return  # have to do error handling
        self.log("Calculating total system demand across all groups...")
        total_predicted_units = 0
        groups_processed = 0
        for grp in self.all_group_names:
            sales_data = db.get_sales_data_by_group(grp)
            # Only process if we have enough data for a WMA calculation
            if len(sales_data) >= window_size:
                f = Forecaster(grp, sales_data)
                future_preds = f.predict_future_sequence(num_days, window_size)
                total_predicted_units += sum(future_preds)
                groups_processed += 1
        self.accuracy_label.configure(text=f"Total System Forecast: {total_predicted_units:.0f} units")
        container = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        summary_text = ( f"TOTAL SYSTEM DEMAND\n"
            f"________________________\n\n"
            f"Forecast Period: {num_days} Days\n"
            f"Categories Calculated: {groups_processed}\n\n"
            f"Total Predicted Unit Volume:\n"
            f"{total_predicted_units:.0f} Units")
        summary_label = ctk.CTkLabel(container, text=summary_text, font=ctk.CTkFont(size=16))
        summary_label.pack(pady=10,expand=True)
        total_label = ctk.CTkLabel(container,text=f"{total_predicted_units:,.0f} Units",font=ctk.CTkFont(size=48, weight="bold"),text_color="#3498db")
        total_label.pack(pady=20)
        self.log(f"System-wide forecast complete. Total volume: {total_predicted_units:.0f} units.")


