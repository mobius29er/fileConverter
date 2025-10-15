import csv
from datetime import datetime

def convert_cashapp_to_tokentax(cashapp_file, tokentax_format_file, output_file):
    """
    Convert CashApp CSV to TokenTax format.
    
    Args:
        cashapp_file: Path to CashApp CSV file
        tokentax_format_file: Path to TokenTax CSV file (for format reference)
        output_file: Path for output CSV file
    """
    
    # Read TokenTax format headers
    with open(tokentax_format_file, 'r', encoding='utf-8') as f:
        tokentax_reader = csv.reader(f)
        tokentax_headers = next(tokentax_reader)
    
    # Read CashApp data
    with open(cashapp_file, 'r', encoding='utf-8') as f:
        cashapp_reader = csv.DictReader(f)
        cashapp_data = list(cashapp_reader)
    
    # Write converted data
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=tokentax_headers)
        writer.writeheader()
        
        for row in cashapp_data:
            # Map CashApp fields to TokenTax format
            # Adjust these mappings based on your actual CSV structures
            converted_row = {
                'Date': row.get('Date', ''),
                'Type': row.get('Transaction Type', ''),
                'Amount': row.get('Amount', ''),
                'Currency': row.get('Currency', 'USD'),
                # Add more field mappings as needed
            }
            
            # Only include fields that exist in TokenTax format
            filtered_row = {k: v for k, v in converted_row.items() if k in tokentax_headers}
            writer.writerow(filtered_row)
    
    print(f"Conversion complete! Output saved to {output_file}")

# Usage
convert_cashapp_to_tokentax('cashapp.csv', 'tokentax.csv', 'output.csv')