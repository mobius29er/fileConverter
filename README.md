# CSV Format Converter 📊

A flexible tool to convert CSV files from one format to another. Perfect for converting CashApp transaction reports to TokenTax format, or any other CSV format transformations.

## Features ✨

- **Drag & Drop Web Interface** - Simple HTML frontend that works in any browser
- **Python Command-Line Tool** - Scriptable converter for automation
- **Format Detection** - Automatically adapts to your target CSV format
- **Transaction Mapping** - Intelligent mapping of transaction types
- **Preview** - See results before downloading

## Quick Start 🚀

### Option 1: Web Interface (Easiest)

1. Open `index.html` in your web browser
2. Drag and drop your **source CSV** file (e.g., CashApp report)
3. Drag and drop your **target format CSV** file (e.g., TokenTax template)
4. Click "Convert to Target Format"
5. Download your converted file!

### Option 2: Python Script (For Automation)

```bash
# Basic usage
python converter.py source.csv target_format.csv output.csv

# Example with your files
python converter.py cash_app_report_1760492693461.csv TokenTaxBlankCSV_1_ex_txn.csv converted_output.csv
```

## Supported Conversions 🔄

Currently optimized for:
- **CashApp → TokenTax**
  - Bitcoin buys/sells
  - Deposits/withdrawals
  - Fees and transaction details
  - Date formatting

The system is designed to be **extensible** - you can easily add mappings for other formats.

## File Formats

### CashApp CSV Format
```csv
Date,Transaction ID,Transaction Type,Currency,Amount,Fee,Net Amount,Asset Type,Asset Price,Asset Amount,Status,Notes
2025-10-09 16:29:46 EDT,,Bitcoin Recurring Buy,USD,-$48.88,-$1.12,-$50.00,BTC,$120963.94,0.00040409,COMPLETE,purchase of BTC
```

### TokenTax CSV Format

https://help.tokentax.co/en/articles/1707630-create-a-manual-csv-report-of-your-transactions
```csv
Type,BuyAmount,BuyCurrency,SellAmount,SellCurrency,FeeAmount,FeeCurrency,Exchange,Group,Comment,Date
Trade,0.4233789,BTC,4320,XRP,0.0010611,BTC,Bittrex,,,1/16/2017 12:53
```

## Transaction Mapping 🗺️

| CashApp Transaction Type | TokenTax Type | Notes |
|--------------------------|---------------|-------|
| Bitcoin Recurring Buy | Trade | Maps BTC amount, USD cost, and fees |
| Bitcoin Buy | Trade | Same as recurring buy |
| Bitcoin Sell | Trade | Maps USD received, BTC sold, and fees |
| Deposits | Deposit | Fiat deposits |
| Withdrawal | Withdrawal | Fiat withdrawals |
| Bitcoin Withdrawal | Withdrawal | Crypto withdrawals |

## Requirements 📋

### For Web Interface
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- No installation needed!

### For Python Script
- Python 3.6 or higher
- No additional packages required (uses only standard library)

## Customization 🛠️

### Adding New Format Mappings

Edit `converter.py` and modify the transaction mapping logic:

```python
# Add your custom transaction type mapping
elif transaction_type == 'Your Custom Type':
    tokentax_row['Type'] = 'Trade'
    tokentax_row['BuyAmount'] = # your logic here
    # ... map other fields
```

### Modifying Date Formats

Update the `parse_cashapp_date()` function:

```python
def parse_cashapp_date(date_str):
    # Customize date parsing logic
    dt = datetime.strptime(date_str, 'your_format_here')
    return dt.strftime('target_format_here')
```

## Troubleshooting 🔧

### "No transactions converted"
- Check that your source file has `COMPLETE` status transactions
- Verify the Transaction Type column values match expected patterns

### "Date format error"
- The script handles most date formats automatically
- Check console output for specific parsing errors

### "File encoding issues"
- Both scripts use UTF-8 encoding
- Try opening your CSV in a text editor and re-saving as UTF-8

## Examples 📝

### Command Line Examples

```bash
# Convert CashApp to TokenTax
python converter.py cashapp_report.csv tokentax_format.csv output.csv

# Batch conversion (PowerShell)
Get-ChildItem *.csv | ForEach-Object {
    python converter.py $_.Name tokentax_format.csv "converted_$($_.Name)"
}

# Batch conversion (Bash)
for file in *.csv; do
    python converter.py "$file" tokentax_format.csv "converted_$file"
done
```

## Project Structure 📁

```
fileConverter/
├── index.html                          # Web interface
├── converter.py                        # Python CLI tool
├── README.md                          # This file
├── cash_app_report_1760492693461.csv # Example source file
└── TokenTaxBlankCSV_1_ex_txn.csv     # Example target format
```

## Tips 💡

1. **Keep a backup** of your original files before converting
2. **Verify the output** by checking a few sample transactions
3. **Use the web interface** for one-off conversions
4. **Use the Python script** for batch processing or automation
5. **The target CSV defines the output format** - make sure it has all the columns you need

## Future Enhancements 🚀

Potential features to add:
- Support for more exchanges (Coinbase, Kraken, Binance, etc.)
- Custom field mapping configuration
- Excel file support
- Validation and error reporting
- Batch processing in web interface

## License 📄

Free to use and modify for your personal or commercial projects.

## Support 🤝

If you encounter issues:
1. Check the console output for error messages
2. Verify your CSV files are properly formatted
3. Make sure transaction types match expected patterns
4. Try the web interface for visual feedback

---

**Happy Converting!** 🎉
