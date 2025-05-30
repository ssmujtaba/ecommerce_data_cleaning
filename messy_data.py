# Import necessary libraries
import pandas as pd  # For data manipulation and CSV output
import numpy as np   # For numerical operations and NaN values
import random        # For generating random values
from faker import Faker  # For generating fake personal data
from datetime import datetime, timedelta  # For date/time operations
import string        # For string operations and character sets

# Initialize Faker generator - creates realistic fake names/addresses
fake = Faker()

# Set random seeds for reproducibility - ensures same results on every run
random.seed(42)
np.random.seed(42)

# Define dataset parameters
num_rows = 30000  # Number of rows to generate
start_date = datetime(2020, 1, 1)  # Earliest possible date
end_date = datetime(2023, 12, 31)  # Latest possible date

# Helper function to create messy names with inconsistent formatting
def messy_name(name):
    """Create variations in name capitalization and spacing"""
    # Generate different name variations
    variations = [
        name.lower(),  # All lowercase
        name.upper(),  # ALL UPPERCASE
        # Random capitalization: each character randomly upper or lower
        ''.join([c.upper() if random.random() > 0.5 else c.lower() for c in name]),
        name.replace(' ', ''),   # Remove spaces
        name.replace(' ', '_'),  # Replace spaces with underscores
        name.replace(' ', '-'),  # Replace spaces with hyphens
        # Add random extra characters to the name
        name + ' ' + ''.join(random.choices(string.ascii_letters, k=random.randint(1, 3))),
    ]
    # Return one random variation from the list
    return random.choice(variations)

# Helper function to create messy email addresses
def messy_email(name):
    """Create email variations with common mistakes"""
    # Split name into parts (first and last)
    parts = name.lower().split()
    first = parts[0] if parts else "user"
    last = parts[1] if len(parts) > 1 else "email"
    
    # Common email domains
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
    
    # Different email format variations
    variations = [
        f"{first[0]}{last}@{random.choice(domains)}",  # jdoe@gmail.com
        f"{first}.{last}@{random.choice(domains)}",    # john.doe@gmail.com
        f"{first}_{last}@{random.choice(domains)}",    # john_doe@gmail.com
        f"{first}{random.randint(1,99)}@{random.choice(domains)}",  # john23@gmail.com
        f"{first[0]}.{last}@{random.choice(domains)}",  # j.doe@gmail.com
        f"{first}{last}@{random.choice(domains)}",      # johndoe@gmail.com (missing dot)
        f"{first}@{random.choice(domains)}",            # john@gmail.com (missing last name)
        f"{last}.{first}@{random.choice(domains)}",     # doe.john@gmail.com
        f"{first}{last[:3]}@{random.choice(domains)}",  # johndoe@yahoo.com (typo in domain)
    ]
    # Introduce errors by sometimes replacing @ with invalid characters
    return random.choice(variations).replace('@', random.choice(['@', '#', '!', '@@', '']))

# Helper function to create messy phone numbers
def messy_phone():
    """Create phone number variations with different formats and errors"""
    # Generate a base 10-digit number
    base_num = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    # Different phone number formatting styles
    formats = [
        f"({base_num[:3]}) {base_num[3:6]}-{base_num[6:]}",  # (123) 456-7890
        f"{base_num[:3]}-{base_num[3:6]}-{base_num[6:]}",     # 123-456-7890
        f"{base_num[:3]}.{base_num[3:6]}.{base_num[6:]}",     # 123.456.7890
        f"+1 {base_num[:3]}-{base_num[3:6]}-{base_num[6:]}",  # +1 123-456-7890
        f"{base_num}",                                        # 1234567890
        f"{base_num[:3]} {base_num[3:6]} {base_num[6:]}",     # 123 456 7890
        f"1-{base_num[:3]}-{base_num[3:6]}-{base_num[6:]}",   # 1-123-456-7890
        f"{base_num[:3]}/{base_num[3:6]}/{base_num[6:]}",     # 123/456/7890
        f"{base_num[:5]}-{base_num[5:]}",                     # 12345-67890
        f"{base_num[:3]}-{base_num[3:]}",                     # 123-4567890
        # Generate completely random phone number
        f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "000-000-0000",  # All zeros
        "123-456-7890",  # Common fake number
        "555-555-5555",  # Another common fake number
        "",              # Empty value
        "N/A",           # Not available indicator
        "missing",       # Missing indicator
    ]
    # Return one random format
    return random.choice(formats)

# Helper function to create messy date strings
def messy_date(date_obj=None):
    """Create date variations with different formats and errors"""
    # If no date provided, generate a random date
    if date_obj is None:
        date_obj = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    
    # Different date formatting styles
    formats = [
        date_obj.strftime("%Y-%m-%d"),     # Standard format: 2022-01-15
        date_obj.strftime("%m/%d/%Y"),      # US format: 01/15/2022
        date_obj.strftime("%d-%m-%Y"),      # European format: 15-01-2022
        date_obj.strftime("%b %d, %Y"),     # Abbreviated month: Jan 15, 2022
        date_obj.strftime("%B %d, %Y"),     # Full month: January 15, 2022
        date_obj.strftime("%m/%d/%y"),      # Short year: 01/15/22
        date_obj.strftime("%d/%m/%y"),      # Short year European: 15/01/22
        date_obj.strftime("%Y%m%d"),        # Numeric: 20220115
        date_obj.strftime("%Y"),            # Only year
        date_obj.strftime("%m-%Y"),         # Month-year only
        date_obj.strftime("%d %b"),         # Day and month only: 15 Jan
        # Generate completely invalid date
        f"{random.randint(1, 12)}/{random.randint(1, 31)}/{random.randint(2020, 2023)}",
        "N/A",              # Not available
        "pending",          # Placeholder text
        "",                 # Empty string
        "01/01/1900",       # Default/invalid date
        "31/02/2022",       # Invalid date (February 31st)
    ]
    # Return one random format
    return random.choice(formats)

# Helper function for delivery status with inconsistencies
def messy_status():
    """Create delivery status with variations"""
    # Valid status options
    statuses = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned", "Pending", "On Hold", "Failed"]
    
    # Create variations of the statuses
    variations = [
        random.choice(statuses),  # Normal status
        random.choice(statuses).upper(),  # ALL CAPS
        random.choice(statuses).lower(),  # all lowercase
        # Status with random number appended
        random.choice(statuses) + " " + str(random.randint(1, 100)),
        # Status with random punctuation
        " ".join([random.choice(statuses), random.choice(["", "!", "!!", "?", "-"])]),
        "N/A",  # Not available
        "",     # Empty string
        " ",    # Space character
        # Boolean-like values
        random.choice(["yes", "no", "true", "false", "1", "0"]),
    ]
    return random.choice(variations)

# Helper function for payment status with inconsistencies
def messy_payment_status():
    """Create payment status with variations"""
    # Valid payment statuses
    statuses = ["Paid", "Unpaid", "Pending", "Refunded", "Failed", "Partially Paid"]
    
    # Create variations
    variations = [
        random.choice(statuses),  # Normal status
        random.choice(statuses).upper(),  # ALL CAPS
        random.choice(statuses).lower(),  # all lowercase
        str(random.choice([True, False])),  # Boolean as string
        str(random.randint(0, 1)),          # Numeric indicator
        random.choice(["yes", "no"]),       # Yes/No
        "N/A",  # Not available
        "",     # Empty string
    ]
    return random.choice(variations)

# Helper function for product names with inconsistencies
def messy_product():
    """Create product names with variations"""
    # Product types
    products = [
        "Smartphone", "Laptop", "Headphones", "Smart Watch", "Tablet", 
        "Camera", "Printer", "Monitor", "Keyboard", "Mouse",
        "USB Cable", "Charger", "Power Bank", "Bluetooth Speaker", "Earbuds"
    ]
    # Product brands
    brands = ["Apple", "Samsung", "Sony", "LG", "Bose", "Dell", "HP", "Lenovo", "Asus", "Acer"]
    
    # Different product naming variations
    variations = [
        f"{random.choice(brands)} {random.choice(products)}",  # Brand + product
        f"{random.choice(products)} {random.choice(['Pro', 'Max', 'Lite', 'Plus', ''])}",  # Product with modifier
        f"{random.choice(products)} - {random.choice(brands)}",  # Product - brand
        f"{random.choice(brands)}-{random.choice(products)}",    # Brand-product
        f"{random.choice(products)}",              # Product only
        f"{random.choice(products).lower()}",      # lowercase product
        f"{random.choice(products).upper()}",      # UPPERCASE PRODUCT
        # Add condition prefix (new, used, etc)
        f"{random.choice(['', 'New ', 'Used ', 'Refurbished '])}{random.choice(products)}",
        # Product with version number
        f"{random.choice(products)} {random.randint(1, 5)}.0",
        f"{random.choice(products)} v{random.randint(1, 5)}",
    ]
    return random.choice(variations)

# Helper function for price formatting with inconsistencies
def messy_price():
    """Create price variations"""
    # Generate a random price
    base_price = round(random.uniform(10, 2000), 2)
    
    # Different price formatting styles
    variations = [
        f"${base_price}",          # $123.45
        f"${base_price:.0f}",      # $123 (no cents)
        f"{base_price} USD",       # 123.45 USD
        f"USD {base_price}",       # USD 123.45
        f"${base_price:.2f}",      # $123.45 (explicit 2 decimals)
        f"{base_price}",           # 123.45 (no currency symbol)
        f"{int(base_price)}",      # 123 (integer)
        f"${base_price * 100} cents",  # $12345 cents
        f"approx ${base_price:.0f}",   # approx $123
        f"{base_price:.0f}.00",        # 123.00
        # Add random cents
        f"{base_price:.0f}.{random.randint(0,99)}",
        "N/A",  # Not available
        "",     # Empty string
    ]
    return random.choice(variations)

# Helper function for quantity with inconsistencies
def messy_quantity():
    """Create quantity variations"""
    variations = [
        str(random.randint(1, 10)),       # Normal quantity
        str(random.randint(1, 10)) + ".0",  # With .0 decimal
        str(random.randint(1, 10)) + ".00", # With .00 decimal
        str(random.choice([1, 2, 3, 5, 10])),  # Common quantities
        "one", "two", "three", "four", "five",  # Word format
        "",     # Empty string
        "N/A",  # Not available
        "0",    # Zero quantity (invalid)
        # Sometimes include 0 which might be invalid
        str(random.randint(0, 1)),  
    ]
    return random.choice(variations)

# Generate the dataset
data = []  # List to store all rows

# Create each row individually
for _ in range(num_rows):
    # Generate clean customer name using Faker
    customer_name = fake.name()
    
    # Generate clean order date (within 2020-2023 range)
    order_date_clean = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    
    # Generate shipping date (usually 1-10 days after order date)
    if random.random() < 0.9:  # 90% of the time
        shipping_date_clean = order_date_clean + timedelta(days=random.randint(1, 10))
    elif random.random() < 0.5:  # 5% of the time (before order date)
        shipping_date_clean = order_date_clean - timedelta(days=random.randint(1, 10))
    else:  # 5% of the time (same as order date)
        shipping_date_clean = order_date_clean
    
    # Create a dictionary representing one row of data
    row = {
        # Customer information
        "customer_name": messy_name(customer_name),
        "customer_email": messy_email(customer_name),
        "customer_phone": messy_phone(),
        
        # Order dates (converted to messy formats)
        "order_date": messy_date(order_date_clean),
        "shipping_date": messy_date(shipping_date_clean),
        
        # Status information
        "delivery_status": messy_status(),
        "payment_status": messy_payment_status(),
        
        # Product information
        "product_ordered": messy_product(),
        "product_price": messy_price(),
        "quantity_ordered": messy_quantity(),
        
        # Additional fields
        "order_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        "shipping_address": fake.address().replace("\n", ", "),
        "billing_address": random.choice([fake.address().replace("\n", ", "), "Same as shipping", ""]),
        "payment_method": random.choice(["Credit Card", "PayPal", "Debit Card", "Bank Transfer", "Cash on Delivery", ""]),
        "discount_code": random.choice(["", "SAVE10", "WELCOME20", "SUMMER25", "FALL15", "WINTER30"]),
        "customer_notes": random.choice(["", "Gift wrapping please", "Leave at front door", "Call before delivery", "Urgent!"]),
        "return_reason": random.choice(["", "Defective", "Wrong item", "Changed mind", "No longer needed"]),
    }
    # Add row to dataset
    data.append(row)

# Create DataFrame from the collected data
df = pd.DataFrame(data)

# Add random missing values (5% of each column)
for col in df.columns:
    # Select 5% of rows randomly and set to NaN
    df.loc[df.sample(frac=0.05).index, col] = np.nan

# Add duplicate rows (2% of total rows)
duplicates = df.sample(n=int(num_rows*0.02))
df = pd.concat([df, duplicates], ignore_index=True)

# Ensure price and quantity are strings to create type inconsistencies
df['product_price'] = df['product_price'].astype(str)
df['quantity_ordered'] = df['quantity_ordered'].astype(str)

# Save to CSV file
df.to_csv('messy_ecommerce_data.csv', index=False)

# Completion message
print("Messy e-commerce dataset with 30,000 rows generated successfully!")
print("File saved as 'messy_ecommerce_data.csv'")