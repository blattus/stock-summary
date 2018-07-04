from alphavantage import *
import csv
try:
	import config
except ImportError:
	print("No config.py file found!")
	exit(1)

API_KEY = config.API_KEY

api_client = Alphavantage(API_KEY)

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
			security = row[2]

			# if we already have the symbol, add the new order info 
			if security in portfolio:
				portfolio[security]['orders'].append(
					{
						'date' : row[0],
						'type' : row[1].lower(),
						'num_shares' : float(row[3]),
						'share_price' : float(row[4]),
						'commission' : float(row[5])
					}
				)
			
			# otherwise create an entry for the symbol and add order info
			else:
				portfolio[security] = {
					'summary' : {
						'symbol' : security,
						'num_shares' : 0,
						'cost_basis' : 0,
						'market_value' : 0,
						'gain_loss' : 0
					},
					'orders' : [
						{
							'date' : row[0],
							'type' : row[1].lower(),
							'num_shares' : float(row[3]),
							'share_price' : float(row[4]),
							'commission' : float(row[5])
						}
					]
				}

	print('portfolio contains '+str(len(portfolio))+' securities.')

	# iterate over the symbols in the portfolio to calculate the portfolio summary
	for security in portfolio:	
		# determine cost basis / number of shares
		cost_basis = 0
		num_shares = 0
		for order in portfolio[security]['orders']:
			if order['type'] == 'buy':
				cost_basis += (order['num_shares'] * order['share_price']) + order['commission']
				num_shares += order['num_shares']
			if order['type'] == 'sell':
				num_shares -= order['num_shares']
		# TODO: handle closed positions 
		
		portfolio[security]['summary']['cost_basis'] = cost_basis	
		portfolio[security]['summary']['num_shares'] = num_shares

	# for market value we could do this in the above loop, but would have to iterate through the 
	# stock quote market_data for every security, so I think this is more efficient
	# note: portfolio.keys() is a list of all symbols in the portfolio

	# make the API call
	market_data = api_client.batch_quote(portfolio.keys())

	for security in market_data:
		price = float(market_data[security]['price'])
		portfolio[security]['summary']['market_value'] = price * portfolio[security]['summary']['num_shares']

	# calculate gain / loss? this might be excessive....
	total_gain_loss = 0
	for security in portfolio:
		portfolio[security]['summary']['gain_loss'] = portfolio[security]['summary']['market_value'] - portfolio[security]['summary']['cost_basis']
		
		# let's look at all open positions
		if portfolio[security]['summary']['num_shares'] > 0:
			total_gain_loss += portfolio[security]['summary']['gain_loss']

	## TODO: add the portfolio summary to the bottom of the table

	print('total gain / loss - ',round(total_gain_loss,2))
	return portfolio




