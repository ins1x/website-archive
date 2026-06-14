#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# launcher_demo on Flask
from flask import Flask, render_template, url_for, request, redirect
# from flask_debugtoolbar import DebugToolbarExtension
import os, sys

# app Config
app = Flask(__name__, template_folder="static/templates")
app.config['DEBUG'] = True
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.secret_key = 'inssixteen'
# Debug toolbar init
# toolbar = DebugToolbarExtension(app)

@app.route('/')
@app.route('/index')
def indexpage():
    return render_template('index.html')

@app.route('/changelog')
def changelogpage():
    return render_template('changelog.html')
	
# Start localserver on run script
if __name__ == '__main__':
	app.run()