import boto3
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


# Helper functions
def listToDict(lst): 
    dict_res = dict.fromkeys(lst,)
    return dict_res 


def input_response(slots_updated):
    response = {
        'dialogAction': {
            'type': "Delegate",
            'slots': slots_updated
        }
    }
    return response


def fulfillment_response():
    fullfill_response = {
        'dialogAction': {
            'type': "Close",
            'fulfillmentState': "Fulfilled",
            'message': "Survey is now complete. Clinician will review responses and send gift card to number on file"
        }
    }
    return fulfill_response


def validate_input(event):
    slots_dict = event['currentIntent']['slots']
    logger.debug(slots_dict)
    

    if slots_dict.get('raceOne') == '1' or slots_dict.get('raceOne') == '2' or slots_dict.get('raceOne') == '3':
        slots_1 = {
            'Slots': {
                'raceTwo': '8',
                'raceThree': '12'
            }
        }
        s1 = slots_1["Slots"]
        slots_dict.update(s1)

    if slots_dict.get('milStatus') == '1':
        slots_2 = {
            'Slots': {
                'milStatusTwo': '1',
                'milService': '5',
                'milDeployment': '1'
            }
        }
        s2 = slots_2["Slots"]
        slots_dict.update(s2)

    if slots_dict.get('activitySexOne') == '2':
        slots_3 = {
            'Slots': {
                'activitySexTwo': '1',
                'activitySexThree': '0',
                'activitySexFour': '0',
                'activitySexFive': '0',
                'activitySexSix': '0'
            }
        }
        s3 = slots_3["Slots"]
        slots_dict.update(s3)
    
    return input_response(slots_dict)


def complete_survey(event):
    logger.debug(event)
    userID = event.get('userId')
    logger.debug(userID)
    intent = event['currentIntent']['name']
    slots = event['currentIntent']['slots']

    # DynamoDB client for posting final survey response
    client = boto3.resource("dynamodb")
    table = client.Table("YSAT")

    table.put_item(
        Item={
            'IntentName': intent,
            'UserID': userID,
            'Slots': slots
        }
    )

    return fulfillment_response
