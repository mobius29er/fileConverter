import csv
from datetime import datetime
import sys
import os

def parse_cashapp_amount(amount_str):
    """Parse CashApp amount string (e.g., '$50.00' or '-$50.00') to float."""
    if not amount_str or amount_str == '':
        return 0.0
    # Remove dollar sign and convert to float
    return float(amount_str.replace('$', '').replace(',', ''))

def parse_cashapp_date(date_str):
    """Convert CashApp date format to TokenTax format (MM/DD/YY HH:MM)."""
    try:
        # CashApp format: "2025-10-09 16:29:46 EDT"
        # Parse both date and time
        date_parts = date_str.split(' ')
        if len(date_parts) >= 2:
            date_part = date_parts[0]  # "2025-10-09"
            time_part = date_parts[1]  # "16:29:46"
            
            dt = datetime.strptime(f"{date_part} {time_part}", '%Y-%m-%d %H:%M:%S')
            # TokenTax format: "MM/DD/YY HH:MM" (e.g., "1/16/17 12:53")
            # Use %m/%d/%y %H:%M format (no leading zeros on month/day)
            formatted = dt.strftime('%m/%d/%y %H:%M')
            # Remove leading zeros from month and day
            parts = formatted.split(' ')
            date_parts = parts[0].split('/')
            month = str(int(date_parts[0]))  # Remove leading zero
            day = str(int(date_parts[1]))    # Remove leading zero
            year = date_parts[2]
            time = parts[1]
            return f"{month}/{day}/{year} {time}"
        else:
            # If only date part, just use that with 00:00 time
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            formatted = dt.strftime('%m/%d/%y 00:00')
            parts = formatted.split(' ')
            date_parts = parts[0].split('/')
            month = str(int(date_parts[0]))
            day = str(int(date_parts[1]))
            year = date_parts[2]
            return f"{month}/{day}/{year} 00:00"
    except:
        try:
            # Fallback to just date parsing
            dt = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')
            formatted = dt.strftime('%m/%d/%y 00:00')
            parts = formatted.split(' ')
            date_parts = parts[0].split('/')
            month = str(int(date_parts[0]))
            day = str(int(date_parts[1]))
            year = date_parts[2]
            return f"{month}/{day}/{year} 00:00"
        except:
            return date_str

def convert_cashapp_to_tokentax(cashapp_file, target_format_file, output_file):
    """
    Convert CashApp CSV to TokenTax format.
    
    Args:
        cashapp_file: Path to source CashApp CSV file
        target_format_file: Path to TokenTax CSV file (defines target format)
        output_file: Path for output CSV file
    
    TokenTax Transaction Types:
        - Trade: Exchanging crypto for crypto or fiat for crypto (and vice versa)
        - Deposit: Moving crypto into an exchange or wallet
        - Withdrawal: Taking crypto out of an exchange or wallet
        - Income: Receiving crypto as income (mining, airdrops, promotions, hard forks)
        - Spend: Spending crypto on goods or services
        - Lost: Crypto lost (e.g., lost private key)
        - Stolen: Crypto stolen
        - Mining: Crypto received as mining reward
        - Gift: Crypto given away
    """
    
    print(f"Reading target format from: {target_format_file}")
    
    # Read TokenTax format headers
    with open(target_format_file, 'r', encoding='utf-8') as f:
        tokentax_reader = csv.reader(f)
        tokentax_headers = next(tokentax_reader)
    
    print(f"Target format headers: {tokentax_headers}")
    print(f"\nReading CashApp data from: {cashapp_file}")
    
    # Read CashApp data
    with open(cashapp_file, 'r', encoding='utf-8') as f:
        cashapp_reader = csv.DictReader(f)
        cashapp_data = list(cashapp_reader)
    
    print(f"Found {len(cashapp_data)} transactions in CashApp file")
    print(f"\nConverting to TokenTax format...")
    
    # Write converted data
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=tokentax_headers)
        writer.writeheader()
        
        converted_count = 0
        skipped_count = 0
        transaction_summary = {}
        
        for row in cashapp_data:
            transaction_type = row.get('Transaction Type', '')
            status = row.get('Status', '')
            
            # Only process completed transactions
            if status != 'COMPLETE':
                skipped_count += 1
                continue
            
            # Initialize TokenTax row with empty strings for all fields
            tokentax_row = {header: '' for header in tokentax_headers}
            
            # Map common fields - Date format: MM/DD/YY HH:MM
            tokentax_row['Date'] = parse_cashapp_date(row.get('Date', ''))
            tokentax_row['Exchange'] = 'CashApp'
            tokentax_row['Comment'] = row.get('Notes', '')
            tokentax_row['Group'] = ''  # Leave blank unless margin trade
            
            # Track transaction types for summary
            mapped_type = None
            
            # Map transaction-specific fields based on TokenTax guidelines
            if 'Bitcoin' in transaction_type and ('Buy' in transaction_type or 'Recurring Buy' in transaction_type):
                # Trade: Exchanging fiat for crypto
                # BuyAmount/BuyCurrency = crypto acquired
                # SellAmount/SellCurrency = fiat spent
                tokentax_row['Type'] = 'Trade'
                tokentax_row['BuyAmount'] = row.get('Asset Amount', '').replace(',', '').strip()
                tokentax_row['BuyCurrency'] = row.get('Asset Type', 'BTC').strip()
                tokentax_row['SellAmount'] = str(abs(parse_cashapp_amount(row.get('Amount', '0'))))
                tokentax_row['SellCurrency'] = 'USD'
                tokentax_row['FeeAmount'] = str(abs(parse_cashapp_amount(row.get('Fee', '0'))))
                tokentax_row['FeeCurrency'] = 'USD'
                mapped_type = 'Trade (Buy)'
                
            elif 'Bitcoin Sell' in transaction_type or 'Bitcoin Sale' in transaction_type:
                # Trade: Exchanging crypto for fiat
                # BuyAmount/BuyCurrency = fiat received
                # SellAmount/SellCurrency = crypto sold
                tokentax_row['Type'] = 'Trade'
                tokentax_row['BuyAmount'] = str(abs(parse_cashapp_amount(row.get('Amount', '0'))))
                tokentax_row['BuyCurrency'] = 'USD'
                tokentax_row['SellAmount'] = row.get('Asset Amount', '').replace(',', '').replace('-', '').strip()
                tokentax_row['SellCurrency'] = row.get('Asset Type', 'BTC').strip()
                tokentax_row['FeeAmount'] = str(abs(parse_cashapp_amount(row.get('Fee', '0'))))
                tokentax_row['FeeCurrency'] = 'USD'
                mapped_type = 'Trade (Sell)'
                
            elif transaction_type == 'Deposits':
                # Check if this is crypto or fiat deposit
                asset_amount = row.get('Asset Amount', '').strip()
                asset_type = row.get('Asset Type', '').strip()
                
                if asset_amount and asset_type:
                    # Crypto deposit - moving crypto into the exchange
                    tokentax_row['Type'] = 'Deposit'
                    tokentax_row['BuyAmount'] = asset_amount.replace(',', '')
                    tokentax_row['BuyCurrency'] = asset_type
                    mapped_type = 'Deposit (Crypto)'
                else:
                    # Fiat deposit - this is just adding funds, not acquiring crypto
                    # Skip this as it's not a taxable event unless used to buy crypto
                    skipped_count += 1
                    continue
                
            elif transaction_type == 'Withdrawal':
                # Fiat withdrawal - taking USD out
                tokentax_row['Type'] = 'Withdrawal'
                tokentax_row['SellAmount'] = str(abs(parse_cashapp_amount(row.get('Net Amount', '0'))))
                tokentax_row['SellCurrency'] = 'USD'
                tokentax_row['FeeAmount'] = str(abs(parse_cashapp_amount(row.get('Fee', '0'))))
                tokentax_row['FeeCurrency'] = 'USD'
                mapped_type = 'Withdrawal (Fiat)'
                
            elif 'Bitcoin Withdrawal' in transaction_type:
                # Crypto withdrawal - taking crypto out of the exchange
                tokentax_row['Type'] = 'Withdrawal'
                tokentax_row['SellAmount'] = row.get('Asset Amount', '').replace('-', '').replace(',', '').strip()
                tokentax_row['SellCurrency'] = row.get('Asset Type', 'BTC').strip()
                tokentax_row['FeeAmount'] = str(abs(parse_cashapp_amount(row.get('Fee', '0'))))
                tokentax_row['FeeCurrency'] = row.get('Asset Type', 'BTC').strip()
                mapped_type = 'Withdrawal (Crypto)'
                
            elif 'Loyalty Rewards' in transaction_type or 'Rewards' in transaction_type:
                # Income: Receiving crypto as a promotion/reward
                asset_amount = row.get('Asset Amount', '').strip()
                if asset_amount and asset_amount != '0':
                    tokentax_row['Type'] = 'Income'
                    tokentax_row['BuyAmount'] = asset_amount.replace(',', '')
                    tokentax_row['BuyCurrency'] = row.get('Asset Type', 'USD').strip()
                else:
                    # No actual crypto received, skip
                    skipped_count += 1
                    continue
                mapped_type = 'Income (Rewards)'
                
            elif 'P2P' in transaction_type:
                # Person-to-person transaction
                amount = parse_cashapp_amount(row.get('Amount', '0'))
                asset_amount = row.get('Asset Amount', '').strip()
                
                if asset_amount:
                    # Crypto P2P
                    if amount < 0:
                        # Sending crypto - could be Gift or Spend
                        tokentax_row['Type'] = 'Gift'
                        tokentax_row['SellAmount'] = asset_amount.replace('-', '').replace(',', '')
                        tokentax_row['SellCurrency'] = row.get('Asset Type', 'BTC').strip()
                    else:
                        # Receiving crypto - Trade or Income
                        tokentax_row['Type'] = 'Income'
                        tokentax_row['BuyAmount'] = asset_amount.replace(',', '')
                        tokentax_row['BuyCurrency'] = row.get('Asset Type', 'BTC').strip()
                    mapped_type = 'P2P'
                else:
                    # Fiat P2P - not taxable crypto event
                    skipped_count += 1
                    continue
                    
            else:
                # Unknown transaction type - skip for now
                print(f"  ⚠ Skipping unknown transaction type: {transaction_type}")
                skipped_count += 1
                continue
            
            # Track transaction type for summary
            if mapped_type:
                transaction_summary[mapped_type] = transaction_summary.get(mapped_type, 0) + 1
            
            # Only write rows with a valid Type
            if tokentax_row['Type']:
                writer.writerow(tokentax_row)
                converted_count += 1
    
    print(f"\n✓ Conversion complete!")
    print(f"✓ Converted {converted_count} transactions")
    print(f"✓ Skipped {skipped_count} transactions (non-taxable or incomplete)")
    print(f"\n📊 Transaction Type Summary:")
    for ttype, count in sorted(transaction_summary.items()):
        print(f"   {ttype}: {count}")
    print(f"\n✓ Output saved to: {output_file}")
    return converted_count

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python converter.py <cashapp_file> <target_format_file> <output_file>")
        print("\nExample:")
        print("  python converter.py cashapp.csv tokentax_format.csv output.csv")
        sys.exit(1)
    
    cashapp_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if not os.path.exists(cashapp_file):
        print(f"Error: CashApp file not found: {cashapp_file}")
        sys.exit(1)
    
    if not os.path.exists(target_file):
        print(f"Error: Target format file not found: {target_file}")
        sys.exit(1)
    
    try:
        convert_cashapp_to_tokentax(cashapp_file, target_file, output_file)
    except Exception as e:
        print(f"\n✗ Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
