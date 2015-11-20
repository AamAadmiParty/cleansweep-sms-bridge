from app import app
from flask import request, jsonify
import shlex
import requests
import uuid


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/sms-bridge/<cleansweep_instance>/", methods=['POST'])
def handle_request(cleansweep_instance):
    password = request.form['secret']

    cleansweep_instance = cleansweep_instance.upper()
    password_in_config = app.config['{0}_PASSWORD'.format(cleansweep_instance)]
    cleansweep_app_url = app.config['{0}_URL'.format(cleansweep_instance)]

    if password != password_in_config:
        return _send_response(401, error="Secret key didn't match for %s." % cleansweep_instance)

    phone = request.form['from']
    message = request.form['message']

    task, argument = message.split(None, 1)

    response = _authorize(task, phone, cleansweep_app_url)
    data = response.json()

    is_authorized = response.status_code == 200
    if is_authorized:
        token = data['token']  # Grab token if authorized
        if task == "send-sms":
            response = _send_sms(token, argument, cleansweep_app_url)
        else:
            response = None
    else:
        return _send_response(response.status_code, reply_sms=True, phone=phone, message=data['error'])

    if response is None:
        return _send_response(404, error="Task not implemented.")

    data = response.json()
    is_successful = response.status_code == 200
    return _send_response(response.status_code, reply_sms=True,
                          phone=phone, message=data['feedback'] if is_successful else data['error'])


def _send_response(status_code, error=None, reply_sms=False, **kwargs):
    """
    Sends a response back to the app.
    :param status_code: Status code of the response.
    :param error: An error message if the request wasn't successful.
    :param reply_sms: A boolean argument. True if you want to send response as a reply sms to the user.
    :param kwargs: Includes phone number and message if reply_sms is set to True.
    :return:
    """
    data = {'payload': {'success': True}}

    if not reply_sms:
        data['payload']['error'] = error  # Stuff users doesn't need to know. So just inform app why the request failed.
    else:
        data['payload']['task'] = 'send'
        data['payload']['messages'] = [{'to': kwargs['phone'], 'message': kwargs['message'], 'uuid': uuid.uuid4().hex}]

    return jsonify(data)


def _authorize(task, phone, cleansweep_app_url):
    """
    Authorize the app by sending client-id and client-secret.
    This also checks if user (phone) has permission for the specified task.

    :param task: The task to perform
    :param phone: User's phone number.
    :param cleansweep_app_url: URL where we send our request for authorization.
    :return: Response from the server in a request object.
    This is what the server is going to return:

    If authorized
    200 OK

    {
        "scope": <scope>,
        "phone": <phone>,
        "token": <token>
    }

    If app does not have permission for the specified scope/task.
    403 Forbidden

    {
        "error": "This app does not have permission for <task>"
    }

    If scope/task is invalid.
    400 Bad Request

    {
        "error": "Invalid scope: <task>"
    }

    If no user can be found from that phone number
    404 Not Found

    {
        "error": "No such user found"
    }

    If user does not have permission for the specified task/scope.
    403 Forbidden

    {
        "error": "The user does not have permission for <task>."
    }
    """
    data = {
        'client-id': app.config['CLIENT_ID'],
        'client-secret': app.config['CLIENT_SECRET'],
        'scope': task,
        'phone': phone
    }
    app.logger.info("URL - %s/api/authorize", cleansweep_app_url)
    app.logger.info("DATA - %s", data)
    response = requests.post('{0}/api/authorize'.format(cleansweep_app_url), data)
    return response


def _send_sms(token, argument, cleansweep_app_url):
    """
    Sends a request to send group sms to all the volunteers of a place.
    :param token: The token to communicate with server
    :param sms_text_parts: The exact sms user sent, split by whitespace.
                            Contains place and the message to send.
    :param cleansweep_app_url: URL where we send our request to send sms.
    :return: Response from the server in a request object.
    This is what the server is going to return:

    If successfully sent
    200 OK

    {
        "feedback": "Your message has been sent to all the volunteers of <sms_text_parts[1]>",
    }

    If token did not match
    400 Bad Request

    {
        "error": "Invalid token: <token>"
    }

    If token gets expired
    400 Bad Request

    {
        "error": "Token expired: <token>"
    }

    If place in sms_text_parts[1] is not a valid place
    400 Bad Request

    {
        "error": "Invalid place: <sms_text_parts[1]>"
    }

    If user does not have permission on that place
    403 Forbidden

    {
        "error": "User does not have permission on: <sms_text_parts[1]>"
    }

    If sms is not configured for that place
    404 Bad Request

    {
        "error": "SMS is not configured for place: <sms_text_parts[1]>"
    }
    """
    try:
        place, message = argument.split(None, 1)
    except ValueError:
        # It is an error if the place is not specified
        return None

    data = {
        'token': token,
        'place': place,
        'message': message
    }
    return requests.post('{0}/api/send-sms'.format(cleansweep_app_url), data)
