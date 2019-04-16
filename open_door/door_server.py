from flask import Flask
app = Flask(__name__)

@app.route('/open_door')
def hello_world():
    return 'Hello, World!'
