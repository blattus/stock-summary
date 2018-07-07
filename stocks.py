from alphavantage import Alphavantage
import csv

try:
	import config
except ImportError:
	print("No config.py file found!")
	exit(1)

API_KEY = config.API_KEY

api_client = Alphavantage(API_KEY)

def parse_security(row):
	if(len(row) != 6):
		raise Exception('Unexpected CSV format')

	return {
		'date' : row[0],
		'type' : row[1].lower(),
		'num_shares' : float(row[3]),
		'share_price' : float(row[4]),
		'commission' : float(row[5])
	}

def determine_cost_basis(position):
	cost_basis = 0
	num_shares = 0
	for order in position['orders']:
		if order['type'] == 'buy':
			cost_basis += (order['num_shares'] * order['share_price']) + order['commission']
			num_shares += order['num_shares']
		if order['type'] == 'sell':
			num_shares -= order['num_shares']
	
	return cost_basis, num_shares

def determine_market_value(portfolio):
	# note: portfolio.keys() is a list of all symbols in the portfolio
	# make the API call
	symbols = portfolio.keys()
	market_data = api_client.batch_quote(symbols)

	for symbol in symbols:
		if(symbol in market_data):
			price = market_data[symbol]['price']
		else:
			price = api_client.get_most_recent_daily_close(symbol)
			
		if price:
			summary = portfolio[symbol]['summary']
			summary['market_value'] = price * summary['num_shares']

def calculate_gain_loss(summary):
	if(summary['market_value']):
		summary['gain_loss'] = summary['market_value'] - summary['cost_basis']
	
def summarize_positions(portfolio):
	# iterate over the symbols in the portfolio to calculate the portfolio summary
	for symbol in portfolio:	
		# determine cost basis / number of shares
		cost_basis, num_shares = determine_cost_basis(portfolio[symbol])
		# TODO: handle closed positions 
		
		portfolio[symbol]['summary']['cost_basis'] = cost_basis	
		portfolio[symbol]['summary']['num_shares'] = num_shares

	# for market value we could do this in the above loop, but would have to iterate through the 
	# stock quote market_data for every security, so I think this is more efficient
	determine_market_value(portfolio)

	# calculate gain / loss? this might be excessive....
	total_gain_loss = 0
	for symbol in portfolio:
		summary = portfolio[symbol]['summary']
		
		calculate_gain_loss(summary)
		
		# let's look at all open positions
		if summary['num_shares'] > 0 and summary['gain_loss']:
			total_gain_loss += summary['gain_loss']

	## TODO: add the portfolio summary to the bottom of the table
	print('total gain / loss - ',round(total_gain_loss,2))

def create_portfolio():
	# Create a portfolio dict grouping orders by symbol
	print('reading portfolio data...')
	portfolio = {}

	with open('portfolio.csv') as csv_file:
		reader = csv.reader(csv_file)
		
		# for now, skip header row. eventually would be cool to parse header row into field names
		# something like this? `headers = f.next().split(',')[1:]` but without the comma splitting
		next(reader, None)

		for raw_row in reader:
			row = list(map(lambda x: x.strip(), raw_row))
			security = parse_security(row)
			symbol = row[2]

			# if we don't have the symbol, add entry to the portfolio
			if symbol not in portfolio:
				portfolio[symbol] = {
					'summary' : {
						'symbol' : symbol,
						'num_shares' : 0,
						'cost_basis' : 0,
						'market_value' : None,
						'gain_loss' : None
					},
					'orders': []
				}

			portfolio[symbol]['orders'].append(security)

	print('portfolio contains '+str(len(portfolio))+' securities.')
	summarize_positions(portfolio)

	return portfolio