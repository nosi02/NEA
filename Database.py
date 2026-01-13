import sqlite3
import hashlib
from datetime import datetime

def create_connection():
    #test to see if can connect to database
    connection = sqlite3.connect('Data/project_data.db')
    connection.close()

def get_sales_data_by_group(group_name):
    connection = sqlite3.connect('Data/project_data.db') #connecting to database file
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT Sales.SaleDate, Sales.QuantitySold FROM Sales
    INNER JOIN Products ON Products.ProductID = Sales.ProductID
    INNER JOIN ProductGroups ON Products.GroupID = ProductGroups.GroupID
    WHERE ProductGroups.GroupName = ? """, (group_name,))# joining the two tables together by linking GroupID #? is a placeholder to pass variables
    results = cursor_obj.fetchall() # creating a list of tuple of result
    connection.close()
    #Sort the data by date
    sorted_data = []
    for date_str,qty in results:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        sorted_data.append((date_obj, qty))
    sorted_data.sort()
    #convert dates back to strings
    final_data_list = []
    for date_obj, qty in sorted_data:
        final_data_list.append((date_obj.strftime('%Y-%m-%d'), qty))
    return final_data_list

def get_inventory_levels():
    inventory_dict = {}
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT ProductGroups.GroupName,IFNULL(Inventory.QuantityOnHand,0)FROM ProductGroups
        LEFT JOIN Inventory ON Inventory.GroupID = ProductGroups.GroupID """  )
    results = cursor_obj.fetchall()
    connection.close()
    # Process results into a dictionary of qty of each grp
    for grp_name,qty in results: #looping through list of tuple
        inventory_dict[grp_name.strip()] = int(qty)
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
    connection.close()
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
        ( SUM(Sales.QuantitySold) * 1.0)/SUM(SUM(Sales.QuantitySold)) 
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
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        sales_by_date[date_obj] = total_qty
    return sales_by_date

def update_mrp_parameters(group_name, new_lead_time, new_safety_stock):
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    find_group = """ SELECT GroupID FROM ProductGroups WHERE GroupName = ? """
    update_parameters = """ UPDATE Parameters 
        SET LeadTime= ?,SafetyStock = ?
        WHERE GroupID = ?"""
    # Find Group ID
    cursor_obj.execute(find_group, (group_name,))
    result = cursor_obj.fetchone()
    #check if there is a result
    if result:
        group_id = result[0]
        # UPDATE
        cursor_obj.execute(update_parameters, (new_lead_time, new_safety_stock, group_id))
        # commit() to save any changes
        connection.commit()
        print(f"Successfully updated parameters for {group_name}")
    connection.close()

def get_all_products():
    connection = sqlite3.connect('Data/project_data.db') #connecting to database file
    cursor_obj = connection.cursor()
    cursor_obj.execute(""" SELECT DISTINCT Products.ProductName, ProductGroups.GroupName FROM Products
    INNER JOIN ProductGroups ON Products.GroupID = ProductGroups.GroupID
    ORDER BY Products.ProductName """)
    results = cursor_obj.fetchall() # creating a list of tuple of result
    connection.close()
    return results

def add_new_product(name, group_name):
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    find_group = """ SELECT GroupID FROM ProductGroups WHERE GroupName = ? """
    insert_product = """ INSERT INTO Products (ProductName, GroupID)
        VALUES (?,?)"""
    # Find Group ID
    cursor_obj.execute(find_group, (group_name,))
    result = cursor_obj.fetchone()
    if result:
        group_id = result[0]
        # UPDATE
        cursor_obj.execute(insert_product, (name, group_id))
        # commit() to save any changes
        connection.commit()
        connection.close()
        return f"Successfully updated parameters for {group_name}"

def delete_product(product_name):
    connection = sqlite3.connect('Data/project_data.db')
    cursor_obj = connection.cursor()
    delete = """ DELETE FROM PRODUCTS WHERE ProductName = ?"""
    cursor_obj.execute(delete,(product_name,))
    connection.commit()
    connection.close()
    return f"Successfully deleted {product_name}"

def get_top_selling_products(limit = 5):
    connection = sqlite3.connect('Data/project_data.db')  # connecting to database file
    cursor_obj = connection.cursor()
    top_5 = (""" SELECT Products.ProductName, SUM(Sales.QuantitySold) FROM Sales
            INNER JOIN Products ON Products.ProductID = Sales.ProductID
            GROUP BY Products.ProductName
            ORDER BY SUM(Sales.QuantitySold)  DESC 
            LIMIT  ? """)
    cursor_obj.execute(top_5, (limit,))
    results = cursor_obj.fetchall()  # creating a list of tuple of result
    connection.close()
    return results

def get_bottom_selling_products(limit = 5):
    connection = sqlite3.connect('Data/project_data.db')  # connecting to database file
    cursor_obj = connection.cursor()
    top_5 = (""" SELECT Products.ProductName, SUM(Sales.QuantitySold) FROM Sales
            INNER JOIN Products ON Products.ProductID = Sales.ProductID
            GROUP BY Products.ProductName
            ORDER BY SUM(Sales.QuantitySold) ASC 
            LIMIT  ? """)
    cursor_obj.execute(top_5, (limit,))
    results = cursor_obj.fetchall()  # creating a list of tuple of result
    connection.close()
    return results

def get_sales_for_last_n_days(days=7):
    connection = sqlite3.connect('Data/project_data.db')  # connecting to database file
    cursor_obj = connection.cursor()
    query = ("""WITH CleanSales AS (SELECT CASE WHEN SaleDate LIKE '__/__/__' THEN 
                        '20' || substr(SaleDate, 7, 2) || '-' || substr(SaleDate, 4, 2) || '-' || substr(SaleDate, 1, 2)
                    ELSE SaleDate END AS FormattedDate,QuantitySold FROM Sales)
        SELECT strftime('%w', FormattedDate) as DayIndex, SUM(QuantitySold) FROM CleanSales
        WHERE FormattedDate >= date('now', '-30 days') GROUP BY DayIndex;""")
    #will need to refernce
    cursor_obj.execute(query)
    results = cursor_obj.fetchall()
    connection.close()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    sales_by_day = {}
    for day in day_names:
        sales_by_day[day] = 0
    for day_index, total_qty in results:
        if day_index == '0' or day_index == 0 or day_index is None:
            continue
        idx = int(day_index) - 1
        if 0 <= idx < len(day_names):
            day_name = day_names[idx]
            sales_by_day[day_name] = total_qty if total_qty else 0
    labels = list(sales_by_day.keys())
    data = list(sales_by_day.values())
    return labels, data

def get_product_suggestions(product_name):
    connection = sqlite3.connect('Data/project_data.db')  # connecting to database file
    cursor_obj = connection.cursor()
    query = (""" SELECT DISTINCT ProductName FROM Products 
                 WHERE GroupID = (SELECT GroupID FROM Products WHERE ProductName = ?) 
                 AND ProductName != ? 
                 LIMIT 3 """)
    cursor_obj.execute(query, (product_name,product_name))
    results = cursor_obj.fetchall()
    final = [row[0] for row in results]
    connection.close()
    return final


def get_product_costs():#find cheapest supplier
    product_costs = {}
    conn = sqlite3.connect('Data/project_data.db')
    cursor = conn.cursor()
    # This query finds the cheapest supplier for every product
    query = (""" SELECT Products.ProductName, Suppliers.SupplierName, MIN(ProductSuppliers.UnitCost) as BestPrice
        FROM ProductSuppliers
        JOIN Products ON ProductSuppliers.ProductID = Products.ProductID
        JOIN Suppliers ON ProductSuppliers.SupplierID = Suppliers.SupplierID
        GROUP BY Products.ProductName; """)
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    for product, supplier, cost in results:
        product_costs[product] = {'supplier': supplier, 'cost': cost}
    return product_costs
def hash_password(password):
    #Converts plain text to hash
    salt = "pharmacy_system_secure_2026_salt"
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def get_stored_hash():
    #Fetches the admin password hash
    # Initializes table with default if missing
    connection = sqlite3.connect('Data/project_data.db')
    cursor = connection.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS SystemSettings (SettingKey TEXT PRIMARY KEY, SettingValue TEXT) 
    """)
    cursor.execute("SELECT SettingValue FROM SystemSettings WHERE SettingKey = 'admin_password_hash'")
    result = cursor.fetchone()
    if result is None:
        default_hash = hash_password("admin123")
        cursor.execute("INSERT INTO SystemSettings VALUES ('admin_password_hash', ?)", (default_hash,))
        connection.commit()
        connection.close()
        return default_hash
    connection.close()
    return result[0]

def update_stored_password(new_password):
    #saves a new password
    new_hash = hash_password(new_password)
    connection = sqlite3.connect('Data/project_data.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE SystemSettings SET SettingValue = ? WHERE SettingKey = 'admin_password_hash'", (new_hash,))
    connection.commit()
    connection.close()


def add_or_update_sale(product_name, qty, date_str):
    connection = sqlite3.connect('Data/project_data.db')
    cursor = connection.cursor()

    # 1. Get ProductID from Name
    cursor.execute("SELECT ProductID FROM Products WHERE ProductName = ?", (product_name,))
    result = cursor.fetchone()

    if not result:
        connection.close()
        return False, f"Product '{product_name}' not found in database."

    product_id = result[0]

    # 2. Check if a sale already exists for this product on this day (to "Update/Adjust")
    cursor.execute("SELECT RowID FROM Sales WHERE ProductID = ? AND SaleDate = ?", (product_id, date_str))
    existing_sale = cursor.fetchone()

    if existing_sale:
        # UPDATE/ADJUST existing record
        cursor.execute("UPDATE Sales SET QuantitySold = ? WHERE RowID = ?", (qty, existing_sale[0]))
    else:
        # INSERT new record
        cursor.execute("INSERT INTO Sales (ProductID, QuantitySold, SaleDate) VALUES (?, ?, ?)",
                       (product_id, qty, date_str))

    connection.commit()
    connection.close()
    return True, "Success"


def bulk_import_sales_csv(file_path):
    import csv
    success_count = 0
    errors = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)  # Assumes headers: ProductName, Quantity, Date
        for row in reader:
            # We reuse the logic above to ensure cleaning/validation
            success, msg = add_or_update_sale(row['ProductName'], row['Quantity'], row['Date'])
            if success:
                success_count += 1
            else:
                errors.append(row['ProductName'])

    return success_count, errors


