# Import necessary libraries
import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import sys
import os

# Install required packages for Excel formatting
try:
    import xlsxwriter
except ImportError:
    print("Installing required Excel packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "xlsxwriter", "openpyxl"])
    import xlsxwriter

# Load the messy dataset
df = pd.read_csv('messy_ecommerce_data.csv')

# Display basic dataset info before cleaning
print("Dataset shape before cleaning:", df.shape)
print("\nFirst 5 rows before cleaning:")
print(df.head())

### 1. Handle Missing Customer Names ###
def is_missing_name(name):
    """Check if a name is missing or empty"""
    if pd.isna(name):
        return True
    if isinstance(name, str) and name.strip() in ['', 'nan', 'NaN', 'N/A']:
        return True
    return False

# Create masks to identify missing names and existing contact info
missing_name_mask = df['customer_name'].apply(is_missing_name)
has_email_mask = df['customer_email'].notna() & (df['customer_email'] != '')
has_phone_mask = df['customer_phone'].notna() & (df['customer_phone'] != '')

# Identify rows that need verification
needs_verification_mask = missing_name_mask & (has_email_mask | has_phone_mask)

# Create a new column to mark names that need verification
df['name_verification'] = 'OK'
df.loc[needs_verification_mask, 'name_verification'] = 'Verify Name with Data Manager'

# Replace missing names with the verification message
df.loc[needs_verification_mask, 'customer_name'] = 'Verify Name with Data Manager'

### 2. Clean and Standardize Customer Names ###
def clean_name(name):
    """Standardize name formatting: Firstname Lastname with proper capitalization"""
    if name == 'Verify Name with Data Manager':
        return name
    if pd.isna(name) or not isinstance(name, str):
        return np.nan
    
    # Remove extra spaces and special characters
    cleaned = re.sub(r'[^a-zA-Z\s]', '', name).strip()
    
    # Split into name parts
    parts = cleaned.split()
    
    # Capitalize first letter of each part, lowercase the rest
    cleaned_parts = []
    for part in parts:
        if len(part) == 0:
            continue
        if len(part) == 1:
            cleaned_parts.append(part.upper())
        else:
            cleaned_parts.append(part[0].upper() + part[1:].lower())
    
    # Rejoin parts with single space
    return ' '.join(cleaned_parts)

# Apply cleaning function to customer names
df['customer_name'] = df['customer_name'].apply(clean_name)

### 3. Clean and Validate Email Addresses ###
def clean_email(email):
    """Standardize email format and validate basic structure"""
    if pd.isna(email) or not isinstance(email, str):
        return np.nan
    if email.strip() == '':
        return np.nan
    
    # Remove any spaces
    cleaned = email.replace(' ', '')
    
    # Fix common domain typos
    domain_fixes = {
        '@gmal.com': '@gmail.com',
        '@gmai.com': '@gmail.com',
        '@yaho.com': '@yahoo.com',
        '@hotmal.com': '@hotmail.com',
        '@otlook.com': '@outlook.com',
        '@aol.cm': '@aol.com',
        '@gmil.com': '@gmail.com',
        '@yhaoo.com': '@yahoo.com'
    }
    
    for wrong, correct in domain_fixes.items():
        if wrong in cleaned:
            cleaned = cleaned.replace(wrong, correct)
    
    # Remove multiple @ symbols
    if cleaned.count('@') > 1:
        cleaned = cleaned.replace('@', '', cleaned.count('@') - 1)
    
    # Remove invalid characters before @ symbol
    if '@' in cleaned:
        parts = cleaned.split('@')
        local_part = re.sub(r'[^a-zA-Z0-9._-]', '', parts[0])
        domain_part = re.sub(r'[^a-zA-Z0-9.-]', '', parts[1]).lower()
        
        # Reconstruct email
        cleaned = f"{local_part}@{domain_part}"
        
        # Validate basic email format
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', cleaned):
            return np.nan
        return cleaned
    return np.nan

# Apply cleaning function to emails
df['customer_email'] = df['customer_email'].apply(clean_email)

### 4. Clean and Standardize Phone Numbers ###
def clean_phone(phone):
    """Standardize phone numbers to country-code format (1-123-456-7890)"""
    if pd.isna(phone) or not isinstance(phone, str):
        return np.nan
    if phone.strip() == '':
        return np.nan
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Skip invalid numbers
    if len(digits) < 7:
        return np.nan
    
    # Handle US/Canada numbers (10 digits)
    if len(digits) == 10:
        return f"1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    
    # Handle numbers with country code (11 digits starting with 1)
    if len(digits) == 11 and digits.startswith('1'):
        return f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    
    # Handle international numbers
    if len(digits) > 7:
        # Format as country code-area code-number
        country_code = digits[:3] if len(digits) > 10 else digits[:1]
        remaining = digits[len(country_code):]
        
        # Format the remaining digits
        if len(remaining) == 10:
            return f"{country_code}-{remaining[:3]}-{remaining[3:6]}-{remaining[6:]}"
        elif len(remaining) == 9:
            return f"{country_code}-{remaining[:3]}-{remaining[3:6]}-{remaining[6:]}"
        elif len(remaining) == 8:
            return f"{country_code}-{remaining[:3]}-{remaining[3:5]}-{remaining[5:]}"
        elif len(remaining) == 7:
            return f"{country_code}-{remaining[:3]}-{remaining[3:]}"
        else:  # Simple format for others
            return f"{country_code}-{remaining}"
    
    return np.nan

# Apply cleaning function to phone numbers
df['customer_phone'] = df['customer_phone'].apply(clean_phone)

### 5. Standardize Date Formats ###
def clean_date(date_str):
    """Convert dates to YYYY-MM-DD format"""
    if pd.isna(date_str) or not isinstance(date_str, str):
        return np.nan
    if date_str.strip() in ['', 'N/A', 'pending', 'nan', 'NaN']:
        return np.nan
    
    # Remove any non-digit characters except separators
    cleaned = re.sub(r'[^\d/\-\.\s]', '', date_str).strip()
    
    # Common date formats to try
    formats = [
        '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%b %d, %Y',
        '%B %d, %Y', '%m/%d/%y', '%d/%m/%y', '%Y%m%d'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # Handle month/year only
    if re.match(r'^\d{1,2}-\d{4}$', cleaned):
        try:
            dt = datetime.strptime(cleaned, '%m-%Y')
            return dt.strftime('%Y-%m') + '-01'
        except ValueError:
            pass
    
    # Handle invalid dates like 31/02/2022
    if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}$', cleaned):
        parts = cleaned.split('/')
        # Try different interpretations
        try:
            # Try MM/DD/YYYY
            year = int(parts[2]) if len(parts[2]) == 4 else int(parts[2]) + 2000
            dt = datetime(year, int(parts[0]), int(parts[1]))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # Try DD/MM/YYYY
                year = int(parts[2]) if len(parts[2]) == 4 else int(parts[2]) + 2000
                dt = datetime(year, int(parts[1]), int(parts[0]))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
    
    # Handle year-only dates
    if re.match(r'^\d{4}$', cleaned):
        try:
            return f"{cleaned}-01-01"
        except ValueError:
            pass
    
    return np.nan

# Apply cleaning to date columns
df['order_date'] = df['order_date'].apply(clean_date)
df['shipping_date'] = df['shipping_date'].apply(clean_date)

### 6. Clean Product Prices ###
def clean_price(price_str):
    """Convert prices to numeric values"""
    if pd.isna(price_str) or not isinstance(price_str, str):
        return np.nan
    if price_str.strip() in ['', 'N/A', 'nan']:
        return np.nan
    
    # Remove currency symbols and text
    cleaned = re.sub(r'[^\d.]', '', price_str)
    
    # Handle empty result
    if cleaned == '':
        return np.nan
    
    try:
        # Convert to float and round to 2 decimals
        return round(float(cleaned), 2)
    except ValueError:
        return np.nan

# Apply cleaning and convert to float
df['product_price'] = df['product_price'].apply(clean_price)

### 7. Clean Quantities ###
def clean_quantity(qty_str):
    """Convert quantities to integers"""
    if pd.isna(qty_str) or not isinstance(qty_str, str):
        return np.nan
    if qty_str.strip() in ['', 'N/A', 'nan']:
        return np.nan
    
    # Convert word numbers to digits
    word_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    if qty_str.lower() in word_to_num:
        return word_to_num[qty_str.lower()]
    
    # Remove decimals and non-digit characters
    cleaned = re.sub(r'[^\d]', '', qty_str)
    
    # Handle empty result
    if cleaned == '':
        return np.nan
    
    try:
        value = int(cleaned)
        return max(1, value)  # Ensure at least 1
    except ValueError:
        return np.nan

# Apply cleaning and convert to integer
df['quantity_ordered'] = df['quantity_ordered'].apply(clean_quantity)

### 8. Calculate Total Order Value ###
# Create new column for total order value
df['total_value'] = df['product_price'] * df['quantity_ordered']

### 9. Detect and Report Outliers ###
def detect_outliers(series, name):
    """Identify and report outliers using IQR method"""
    # Skip if series is empty
    if series.dropna().empty:
        print(f"\nNo data available for outlier detection in {name}")
        return pd.Series([])
    
    # Calculate quartiles and IQR
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    # Ensure non-negative bounds
    lower_bound = max(Q1 - 1.5 * IQR, 0)  # Can't have negative prices/quantities
    upper_bound = Q3 + 1.5 * IQR
    
    # Find outliers
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    
    print(f"\nOutlier Report for {name}:")
    print(f"- Lower bound: {lower_bound:.2f}, Upper bound: {upper_bound:.2f}")
    print(f"- Number of outliers: {len(outliers)}")
    
    # Plot distribution
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=series)
    plt.title(f'Distribution of {name}')
    plt.savefig(f'{name}_distribution.png', bbox_inches='tight')
    plt.close()
    
    return outliers

# Detect outliers in prices and quantities
price_outliers = detect_outliers(df['product_price'].dropna(), 'product_price')
quantity_outliers = detect_outliers(df['quantity_ordered'].dropna(), 'quantity_ordered')
total_value_outliers = detect_outliers(df['total_value'].dropna(), 'total_value')

### 10. Identify Duplicates ###
# Find duplicate rows based on key columns
duplicate_mask = df.duplicated(subset=['customer_email', 'order_date', 'product_ordered'], keep=False)
duplicates = df[duplicate_mask]

print(f"\nDuplicate Report:")
print(f"- Total duplicate rows: {len(duplicates)}")
print("- Potential reasons for duplicates:")
print("  * Same customer ordering same product on same day")
print("  * Data entry errors creating duplicate records")
print("  * System glitches during order processing")
print("  * Retry transactions due to payment failures")

# Create a duplicate flag column
df['duplicate_flag'] = duplicate_mask

### 11. Save Cleaned Data to Excel with Formatting ###
try:
    # Create Excel writer object
    with pd.ExcelWriter('cleaned_ecommerce_data.xlsx', engine='xlsxwriter') as writer:
        # Write cleaned data to Excel
        df.to_excel(writer, sheet_name='Cleaned Data', index=False)
        
        # Access the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Cleaned Data']
        
        # Define formats
        red_format = workbook.add_format({'bg_color': '#FFC7CE'})  # Light red
        header_format = workbook.add_format({
            'bold': True, 
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            # Skip if column has no data
            if df[col].empty:
                continue
            # Get max length in column
            max_len = max(
                df[col].astype(str).apply(len).max(), 
                len(col)
            ) + 2
            worksheet.set_column(i, i, max_len)
        
        # Apply red background for names needing verification
        for row_idx in range(1, len(df) + 1):
            if df.loc[row_idx-1, 'name_verification'] == 'Verify Name with Data Manager':
                worksheet.write(row_idx, 0, df.loc[row_idx-1, 'customer_name'], red_format)
    
    print("\nCleaning complete! Final dataset shape:", df.shape)
    print("Cleaned data saved to 'cleaned_ecommerce_data.xlsx'")
    print("Name verification issues highlighted in red")

except Exception as e:
    print(f"\nError creating Excel file: {e}")
    print("Saving to CSV instead...")
    df.to_csv('cleaned_ecommerce_data.csv', index=False)
    print("Cleaned data saved to 'cleaned_ecommerce_data.csv'")

print(f"Found {len(price_outliers)} price outliers and {len(quantity_outliers)} quantity outliers")
print(f"Found {len(duplicates)} duplicate rows")