import boto3
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# ---Main Handler---
def lambda_handler(event, context):
    logger.debug(event)
    try:
        if event['invocationSource'] == 'DialogCodeHook':
            intent_name = event['currentIntent']['name']
            if intent_name == 'intake':
                return validate_input(event)
            elif intent_name == 'test':
                return validate_input(event)
        else:
            raise ValueError('Must be Fullfillment')

    except ValueError:
        if event['invocationSource'] == 'FulfillmentCodeHook':
            intent_name = event['currentIntent']['name']
            if intent_name == 'intake':
                return complete_survey(event)
            elif intent_name == 'test':
                return complete_survey(event)

    else:
        logger.debug(event)


def input_response(slots):
    response = {
        'dialogAction': {
            'type': "Delegate",
            'slots': slots
        }
    }
    return response


def fulfillment_response(fullfillment_state, message):
    filled_response = {
        'dialogAction': {
            'type': "Close",
            'fulfillmentState': fullfillment_state,
            'message': message + '. Survey is now complete. Clinician will review responses and send gift card to '
                                 'number on file'
        }
    }
    return filled_response


def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res


def validate_input(event):
    userID = event.get('userId')
    intent = event['currentIntent']['name']
    slots_current = event['currentIntent']['slots']

    # DynamoDB client
    client = boto3.resource("dynamodb")
    table = client.Table("DBHDS_YSAT")

    # Efficiency logic
    if slots_current['raceOne'] != '4':
        table.put_item(
            Item={
                'IntentName': intent,
                'UserID': userID,
                'Slots': {
                    'raceTwo': '8',
                    'raceThree': '12'
                }
            }
        )

    elif slots_current['milStatus'] == '1':
        table.put_item(
            Item={
                'IntentName': intent,
                'UserID': userID,
                'Slots': {
                    'milStatus': '1',
                    'milService': '5',
                    'milDeployment': '1'
                }
            }
        )

    elif slots_current['activitySexOne'] == '2':
        table.put_item(
            Item={
                'IntentName': intent,
                'UserID': userID,
                'Slots': {
                    'activitySexTwo': '1',
                    'activitySexThree': '0',
                    'activitySexFour': '0',
                    'activitySexFive': '0',
                    'activitySexSix': '1'
                }
            }
        )

    # DynamoDB Session Data
    resp = table.query(KeyConditionExpression=Key('UserID').eq(userID))
    slots_session = resp['Items'][0]['Slots']

    # Merge Slot Dictionaries
    slots = merge_dicts(slots_current, slots_session)
    table.put_item(
        Item={
            'IntentName': intent,
            'UserID': userID,
            'Slots': slots
        }
    )
    return input_response(slots)


def complete_survey(event):
    userID = event.get('userId')
    intent = event['intentName']
    sessionID = event['sessionId']
    slots = event['recentIntentSummaryView']['slots']
    fullfillment_state = event['recentIntentSummaryView']['fullfillmentState']
    message = event['recentIntentSummaryView']['confirmationStatus']

    # DynamoDB client for posting final survey response
    client = boto3.resource("dynamodb")
    table = client.Table("DBHDS_YSAT")

    table.put_item(
        Item={
            'IntentName': intent,
            'SessionID': sessionID,
            'UserID': userID,
            'Slots': slots
        }
    )

    fulfillment_response(fullfillment_state, message)
