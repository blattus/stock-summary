portfolio = {}
portfolio['test'] = {
			'summary' : {
				'num_shares' : 15,
				'cost_basis' : 0,
				'market_value' : 20,
				'gain_loss' : 0
			},
			'orders' : [
				{
					'date' : 0,
					'type' : 'buy',
					'num_shares' : 20,
					'share_price' : 0,
					'commission' : 0
				},
				{
					'date' : 0,
					'type' : 'sell',
					'num_shares' : 5,
					'share_price' : 0,
					'commission' : 0
				}
			]
		}

# calculate cost basis
cost_basis = 0
for order in portfolio['test']['orders']:
	if order['type'] == 'buy':
		cost_basis += (order['num_shares'] * order['share_price']) + order['commission']

# calculate number of shares
num_shares = 0
for order in portfolio['test']['orders']:
	if order['type'] == 'buy':
		num_shares += order['num_shares']
	if order['type'] == 'sell':
		num_shares -= order['num_shares']

# calculate market value -- API call