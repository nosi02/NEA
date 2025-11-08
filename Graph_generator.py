# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import Database as db

# def plot_total_sales_chart():
#     """
#     Generates and displays a bar chart of total sales per day for all products.
#     """
#     print("Generating total sales chart...")

    # 1. Get data from the database
    # This function returns a dict like {<date_obj>: total_qty, ...}
    # sales_data = db.get_total_sales_per_day()
    #
    # if not sales_data:
    #     print("No sales data found to plot.")
    #     return

    # 2. Prepare data for matplotlib
    # Sort the dictionary by date
    #sorted_items = sorted(sales_data.items())

    # Unpack the dates and quantities into separate lists
    # dates = [item[0] for item in sorted_items]
    # units = [item[1] for item in sorted_items]

    # 3. Create the bar chart
    # plt.figure(figsize=(15, 7))  # Make the figure wider for readability
    # plt.bar(dates, units, color='royalblue', width=0.9)
    #
    # plt.xlabel("Date")
    # plt.ylabel("Total Quantity Sold")
    # plt.title("Total Unit Sales Per Day (All Products)")

    # --- Format the x-axis to show dates nicely ---

    # Set the formatter to display dates as 'dd/mm/yy'
    # date_format = mdates.DateFormatter('%d/%m/%y')
    # plt.gca().xaxis.set_major_formatter(date_format)

    # Set the locator to show a tick mark (e.g., every 5 days)
    # Use DayLocator, WeekLocator, or MonthLocator as needed
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))

    # Rotate date labels automatically to prevent overlap
    #plt.gcf().autofmt_xdate()

    #plt.grid(axis='y', linestyle='--', alpha=0.7)
    #plt.tight_layout()  # Adjust plot to prevent labels being cut off

    # Finally, display the plot
    #plt.show()

# --- To use this ---
# Call this function from your main script to show the chart
#
# if __name__ == "__main__":
#     plot_total_sales_chart()