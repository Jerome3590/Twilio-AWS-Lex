import json
import logging
import boto3
from boto3.dynamodb.conditions import Key


logger =logging.getLogger()
logger.setLevel(logging.DEBUG)
# --- Main handler ---


def lambda_handler(event, context):
    logger.debug('event.intentName={}'.format(event['intentName']))
    return dispatch(event)


def dispatch(intent_request):
    intent_name = intent_request['intent']
    if intent_name == 'intake':
        return complete_survey(intent_request)
    elif intent_name == 'test':
        return complete_survey(intent_request)


# --- Helpers that build all of the responses ---

def test_comms(intent_request):
    intent = intent_request['intent']
    message = intent_request['botResponse']
    sessionID = intent_request['sessionId']
    slots = intent_request['slots']
    session_attributes = {}

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
                 'Fulfilled',
                 {
                 'contentType': 'PlainText',
                 'content': message }
                 )
 


def complete_survey(intent_request):
    userID = intent_request.get('userId')
    intent = intent_request['intent']
    message = intent_request['inputTranscript']
    sessionID = intent_request['sessionId']
    slots = intent_request['slots']
    session_attributes = {}

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
                 'Fulfilled',
                 {
                 'contentType': 'PlainText',
                 'content': message }
                 )
 

def close(session_attributes, fulfillment_state, message):
    response = {
           'dialogAction': {
           'type': 'Close',
           'fulfillmentState': fulfillment_state,
            'message': message
           }
    }
    return response
