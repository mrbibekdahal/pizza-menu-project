import csv

menu = [
    ["beef_sizzler", 8.99],
    ["chicken_sizzler", 10.99],
    ["hawaiian", 9.99],
    ["meat_feast", 9.99],
    ["small_beef_sizzler", 8.99],
    ["small_chicken_sizzler", 10.99],
    ["small_hawaiian", 9.99],
    ["small_meat_feast", 9.99],
    ["small_veg_sizzler", 4.99],
    ["small_veg_supreme", 4.99],
    ["veg_sizzler", 9.99],
    ["veg_supreme", 9.99]
]


with open("pizza_prices.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Pizza", "Price"])  
    writer.writerows(menu)

print("pizza_prices.csv created successfully!")