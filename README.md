# cleansweep-sms-bridge
A SMS interface to cleansweep app

We are using [SMSSyc] (http://smssync.ushahidi.com), A SMS gateway for Android, to send incoming SMSes to our server.

The idea is to intreact with the cleansweep app offline by sending messages to the phone number where the gateway app is installed.

Gateway app then make POST requests to our server. We process the SMS and communicate with cleansweep using its APIs.

SMS format

`<scope> <arguments>`

For example, if the user wants to send sms to all the volunteers of a place:

`send-sms <place> <message>`

# Endpoint

```
POST /sms-bridge/<cleansweep_instance>/

{
    "secret": "VEmleukjCvpNoVnmeIIGFaCuIJckjTBR",
    "from": "<phone-number>",
    "message": "send-sms DL hello"
}
```

We run different instances of cleansweep. On heroku, localhost etc. So we specify which instance to use in endpoint.
`from` is phone number of the user who sent the message.


Response (Format strict to SMSSync)
```
200 OK

{
  "payload": {
    "messages": [
      {
        "message": "Message sent.", 
        "to": "<phone-number>", 
        "uuid": "37c41769bc86436282b298047e2f41c9"
      }
    ], 
    "success": true, 
  }
}
```

Where `uuid` is a unique id SMSSync demands. The `message` gets sent to `to` as reply.

# Security measures
To use cleansweep APIs we must first add the app to its trusted apps list.

```
TRUSTED_APPS = [
    {
        'app-name': 'cleansweep-sms-bridge',
        'client-id': 'xSbAMFEJlFrZUFyV',
        'client-secret': 'VEmleukjCvpNoVnmeIIGFaCuIJckjTBR',
        'scope': ['send-sms', 'send-email'],  #Scopes allowed to this app
        'ips': ['']
    }
]
```

We then ask for the token from cleansweep to make API requests.

# Setup
We'll need:

- Python 2.7+
- pip
- virtualenv

Clone repository 
```
$ git clone https://github.com/AamAadmiParty/cleansweep-sms-bridge.git
$ cd cleansweep-sms-bridge
```

Setup virtualenv
```
$ virtualenv . 
```

Activate it
```
$ source bin/activate
```

Install required packages
```
$ pip install -r requirements.txt
```

Run
```
$ python run.py 
```
