from app import app
from flask import request, jsonify


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/sms-bridge/", methods=['GET'])
def handle_request():
    # Just ffs
    if 'password' not in request.args or not request.args.get('password') or \
            'phone' not in request.args or not request.args.get('phone') or \
            'message' not in request.args or not request.args.get('message'):
        return jsonify(), 400

    password = request.args.get('password')
    if password != app.config['PASSWORD']:
        return jsonify(), 401

    phone = request.args.get('phone')
    message = request.args.get('message')
    # TODO Break the message into parts and then do what's asked in some another function
    return jsonify({'received': True, 'message': message})
