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

#prevent data overlap
#plt.gcf().autofmt_xdate()

# if want to use a line graph
# plt.plot(x, y)
# plt.xlabel("X-axis")        # Label for the X-axis
# plt.ylabel("Y-axis")        # Label for the Y-axis
# plt.title("Any suitable title")  # Chart title
# plt.show()
# Print how many units each day
#print("\n=== Sales by Date (Ordered) ===")
#for date_obj, total in Sum_of_Qty_Sold.items():
    #print(f"{date_obj.strftime('%d/%m/%y')}: {total} units")

#print(f"\nTotal: {sum(Sum_of_Qty_Sold.values())} units")