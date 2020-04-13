import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
        body="Join Earth's mightiest heroes. Like Kevin Bacon.",
        from_='+18042512876',
        to='+18048733575'
)

print(message.sid)
