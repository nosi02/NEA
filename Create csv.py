import csv

# This script creates a clean CSV file to test your NEA import feature.
# It ensures the format is perfect and avoids Mac TextEdit issues.

data = [
    ["ProductName", "Quantity", "Date"],
    ["Allergy Medication", "15", "2026-01-10"],
    ["Pain Relief", "22", "2026-01-10"],
    ["Vitamins", "5", "2026-01-11"],
    ["Allergy Medication", "10", "2026-01-11"],
    ["Antibiotics", "8", "2026-01-12"]
]

file_name = "test_sales.csv"

try:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print(f"Successfully created {file_name}!")
    print("You can now select this file using your 'Bulk Import CSV' button.")
except Exception as e:
    print(f"Error creating file: {e}")