"""
Simple API client for the AlphaVantage stock API. 

"""

import json
import requests
import time

class Alphavantage(object):
	
	# initiate the class with the user's API key
	def __init__(self,key):

		# TODO: perform some validation on the key here
		self.api_key = key	
		self.SECONDS_PER_REQUEST = 1 # Alphavantage has a rate limit of 1 call/s on free version

	def intraday(self,symbol,interval):
		if interval not in [1,5,15,30,60]:
			print('assuming default interval of 5 min')
			interval = '5min'
		else:
			interval = str(interval)+'min'

		params = {
			'function' : 'TIME_SERIES_INTRADAY',
			'symbol' : symbol,
			'interval' : interval
		}

		return(self.get_results_with_retry(params))

	# TODO: is there some way to consolidate with function decorators?
	def daily(self,symbol):
		params = {
			'function' : 'TIME_SERIES_DAILY',
			'symbol' : symbol
		}
		return self.get_results_with_retry(params)

	def get_most_recent_daily_close(self, symbol):
		results = self.daily(symbol)
		key = None
		for k in results.keys():
			if 'Time Series' in k:
				key = k
		if key:
			times = results[key].keys()
			times.sort(reverse=True)
			return float(results[key][times[0]]['4. close'])

	def daily_adjusted(self,symbol):
		params = {
			'function' : 'TIME_SERIES_DAILY_ADJUSTED',
			'symbol' : symbol
		}

		return(self.get_results_with_retry(params))

	def weekly(self,symbol):
		params = {
			'function' : 'TIME_SERIES_WEEKLY',
			'symbol' : symbol
		}

		return(self.get_results_with_retry(params))

	def batch_quote(self,symbols):
		params = {
			'function' : 'BATCH_STOCK_QUOTES',
		}
		
		# for the batch quote, need to provide a single param with comma-separated symbols
		if len(symbols) == 1:
			params['symbols'] = symbols
		else:
			params['symbols'] = ','.join(symbols)

		api_results = self.get_results_with_retry(params)
		batch_quotes = {}
		
		for result in api_results['Stock Quotes']:
			symbol = result['1. symbol']
			batch_quotes[symbol] = {
				'symbol' : symbol,
				'price' : float(result['2. price']),
				'volume' : result['3. volume'],
				'timestamp' : result['4. timestamp']
			}

		return(batch_quotes)

	def crypto_usd(self,from_currency):
		""" 
		Returns the current value of 1 unit of the specified cryptocurrency in USD. 
		For now this uses the FX feature of AlphaVantage but would likely be 
		more correct using the dedicated crypto endpoints
		"""

		params = {
			'function' : 'CURRENCY_EXCHANGE_RATE',
			'from_currency' : from_currency,
			'to_currency' : 'USD'
		}

		result = self.get_results_with_retry(params)
		if('Realtime Currency Exchange Rate' in result):
			crypto_usd = result['Realtime Currency Exchange Rate']['5. Exchange Rate']

		return(crypto_usd)

	# get results with retry for Rate Limit Exceeded
	def get_results_with_retry(self, kwargs):
		time.sleep(self.SECONDS_PER_REQUEST)
		results = self.get_results(kwargs)
		while('Information' in results and '/premium' in results['Information']):
			print('API Rate Limit Exceeded')
			time.sleep(self.SECONDS_PER_REQUEST)
			results = self.get_results(kwargs)
		
		return results

	# get API results
	def get_results(self,kwargs):

		api_endpoint = 'https://www.alphavantage.co/query?'
		params = {}
		params['apikey'] = self.api_key

		# TODO: validation?
		for key, value in kwargs.items():
			params[key] = value

		result = requests.get(url=api_endpoint, params=params)

		return result.json()


""" possible functions:
TIME_SERIES_INTRADAY
TIME_SERIES_DAILY
TIME_SERIES_DAILY_ADJUSTED
TIME_SERIES_WEEKLY
BATCH_STOCK_QUOTES -- takes `symbols`, returns quote for each with timestamp
"""
