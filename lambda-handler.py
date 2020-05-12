import json
import logging
import boto3
from boto3.dynamodb.conditions import Key


logger =logging.getLogger()
logger.setLevel(logging.DEBUG)
# --- Main handler ---


def lambda_handler(event, context):
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)


def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'intake':
        return complete_survey(intent_request)
    elif intent_name == 'test':
        return complete_survey(intent_request)


# --- Helpers that build all of the responses ---

def complete_survey(intent_request):
    userID = intent_request['currentIntent']['userId']
    intent = intent_request['currentIntent']['intentName']
    message = intent_request['currentIntent']['botResponse']
    sessionID = intent_request['currentIntent']['sessionId']
    slots = intent_request['currentIntent']['slots']

    #DynamoDB session data
    client = boto3.resource("dynamodb")
    table = client.Table("DBHDS_YSAT")
    resp = table.query(KeyConditionExpression=Key('UserID').eq(userID))
    slotSessionAttributes = resp['Items'][0]['Slots']
    session_attributes = slotSessionAttributes
    
    #DynamoDB POST data
    table.put_item(
        Item={
        'IntentName': intent,
        'SessionID': sessionID,
        'UserID': userID,
        'Slots': slots
        }

    )
    
    #return response with session data
    return close(
                 session_attributes,
                 'Fulfilled',{
                 'contentType': 'PlainText',
                 'content': message }
                 )
 

def close(session_attributes, fulfillment_state, message):
    response = {
       'sessionAttributes': session_attributes,
       'dialogAction': {
           'type': 'Close',
           'fulfillmentState': fulfillment_state,
           'message': message
       }
    }
    return response
