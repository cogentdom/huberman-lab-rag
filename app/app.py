from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import openai
import redis
import numpy as np
from typing import List
import pickle
from utils import process_query

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = process_query(user_query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=8000, debug=debug_mode) 