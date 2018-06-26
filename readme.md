# Introduction

This project provides a simple (some would argue elementary) view into financial portflio performance based on a running ledger of "Buy" and "Sell" orders. I made this because I missed the old Google Finance Summary view that gave me a quick glance into overall performance for stocks I hold. This is completely as-is and probably has a bunch of bugs, but it works for my needs!

Market data is obtained using the Alpha Vantage API through a a small API client (`alphavantage.py`)

# Dependencies
- Python3
- flask
- requests

# Running
- Obtain an [Alpha Vantage](https://www.alphavantage.co/) API key
- Add a `config.py` file to the root directory with a single line: `API_KEY = [[ your alpha vantage API key ]]`

- Add your ledger to a `portfolio.csv` file with the format `date`,`order_type`,`symbol`,`num_shares`,`share_price`,`commission`
	- `date` - YYYY-MM-DD as [ISO-8601](https://xkcd.com/1179/) intended
	- `order_type` - "Buy" or "Sell"
	- `symbol` - ticker symbol of the security
	- `num_shares` - number of shares bought / sold
	- `share_price` - price per share
	- `commission` - commission (if any)

- `python server.py`
- Go to the addres shown in your terminal window to view the summary table

# Todo
- Add support for stock dividends / cash balance (these can be entered manually in the ledger as a $0 "Buy" for now)
- Extend API client to include coverage of other endpoints (like crypto)
- Add sort of basic things like being able to sort the table, add securities via web FE, etc.
- Write tests


