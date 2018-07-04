from flask import Flask, request, abort, render_template
from stocks import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def homepage():
	portfolio = create_portfolio()
	return render_template('index.html', portfolio=portfolio, title='Home')



if __name__ == '__main__':
	app.run()