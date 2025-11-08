import sqlite3
from datetime import datetime

def get_sales_data_by_group(group_name):
    connection = sqlite3.connect('Data/project_data.db') #connecting to database file
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT Sales.SaleDate, Sales.QuantitySold FROM Sales
    INNER JOIN Products ON Products.ProductID = Sales.ProductID
    INNER JOIN ProductGroups ON Products.GroupID = ProductGroups.GroupID
    WHERE ProductGroups.GroupName = ?
    ORDER BY Sales.SaleDate """, (group_name,)
                       )# joining the two tables together by linking GroupID #? is a placeholder
    results = cursor_obj.fetchall() # creating a list of tuple of result
    connection.close()
    return results

def get_inventory_levels():
    inventory_dict = {}
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT ProductGroups.GroupName,Inventory.QuantityOnHand FROM ProductGroups
        INNER JOIN Inventory ON Inventory.GroupID = ProductGroups.GroupID  """  )
    results = cursor_obj.fetchall()
    connection.close()
    # Process results into a dictionary of qty of each grp
    for grp_name,qty in results: #looping through list of tuple
        inventory_dict[grp_name] = qty
    return inventory_dict

def get_mrp_parameters():
    lead_times = {}
    safety_stocks = {}
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT ProductGroups.GroupName,Parameters.SafetyStock,Parameters.LeadTime 
    FROM Parameters
    INNER JOIN ProductGroups ON ProductGroups.GroupID = Parameters.GroupID  """)
    results = cursor_obj.fetchall()
    connection.close()
    # Process results into a dictionaries of lead time and safety stock for each grp
    for grp_name, safety, lead in results:
        lead_times[grp_name] = lead
        safety_stocks[grp_name] = safety
    return lead_times, safety_stocks

def get_all_group_names():
    group_list = []
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT GroupName FROM ProductGroups""")
    results = cursor_obj.fetchall()
    # Process results into a dictionary of just all the product grp names
    for grp_name in results:
        group_list.append(grp_name[0])
    return group_list

def get_sales_mix():
    sales_mix = {}
    connection = sqlite3.connect('Data/project_data.db')  # connecting to database file
    cursor_obj = connection.cursor()
    # Query calculates the sales % for each product within its group and uses a window function to get group total
    # (Individual Product's Total Sales) / (That Product's Group Total Sales)
    cursor_obj.execute(""" SELECT ProductGroups.GroupName, Products.ProductName,
    (SUM(Sales.QuantitySold) * 1.0)/SUM(SUM(Sales.QuantitySold)) 
    OVER (PARTITION BY ProductGroups.GroupName) AS SalesMix FROM Sales
        INNER JOIN Products ON Products.ProductID = Sales.ProductID
        INNER JOIN ProductGroups ON Products.GroupID = ProductGroups.GroupID
        GROUP BY ProductGroups.GroupName, Products.ProductName  """ )  #multppy by 1.0 to use float division
    results = cursor_obj.fetchall()
    connection.close()
    # Process results into a nested dictionary of group name
    # and then a dictionary of products within grp and their sales %
    for grp_name, product, percent in results:
        if grp_name not in sales_mix:
            sales_mix[grp_name] = {}
        sales_mix[grp_name][product] = percent
    return sales_mix


def get_total_sales_per_day():
    sales_by_date = {}
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT SaleDate, SUM(QuantitySold) AS TotalQty 
        FROM Sales WHERE QuantitySold > 0
        GROUP BY SaleDate
        ORDER BY SaleDate; """)
    results = cursor_obj.fetchall()
    connection.close()
    # Process results into a dictionary of total sales for each data
    for date_str, total_qty in results:
        # Convert the date string (e.g., 'dd/mm/yy') to a datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%y').date()
        sales_by_date[date_obj] = total_qty
    return sales_by_date

