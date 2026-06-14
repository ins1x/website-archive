# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import url_for
import os.path

# configuration
DATABASE = 'sitebase.db'

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	try:
		return render_template('index.html')	
	except TemplateNotFound:
		abort(404)

if __name__ == '__main__':
	app.run(debug=True)
