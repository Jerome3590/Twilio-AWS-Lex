import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

phone_number = client.lookups \
    .phone_numbers('+18048733575') \
    .fetch(add_ons=['ekata_reverse_phone'], type=['carrier'])

print(phone_number.add_ons)