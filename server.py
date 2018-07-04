from flask import Flask, request, abort, render_template
from stocks import portfolio

app = Flask(__name__)
global portfolio

@app.route('/', methods=['GET'])
def homepage():
	if request.method == 'GET':
		return render_template('index.html', portfolio=portfolio, title='Home')
	else:
		abort(400)


if __name__ == '__main__':
	app.run()