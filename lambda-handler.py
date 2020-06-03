import boto3
import logging
from boto3.dynamodb.conditions import Key

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
            elif intent_name == 'exit':
                return exit_survey(event)
        else:
            raise ValueError('Must be Fullfillment')

    except ValueError:
        logger.debug(event)

    else:
        logger.debug(event)


def input_response(slots_updated):
    response = {
        'dialogAction': {
            'type': "Delegate",
            'slots': slots_updated
        }
    }
    return response
    
    
def check_session(event):
    userID = event.get('userId')
    slots_dict_d1 = event['currentIntent']['slots']
        
    try:
        #DynamoDB session data
        client = boto3.resource("dynamodb")
        table = client.Table("Processing")
        resp = table.query(KeyConditionExpression=Key('UserID').eq(userID))
        slots_dict_d2 = resp['Items'][0]['Slots']
        logger.debug(slots_dict_d2)
        
        if len(slots_dict_d2) > len(slots_dict_d1):
            slots_dict_d1.update(slots_dict_d2)
            slots_dict = slots_dict_d1
            return slots_dict
    
    except ValueError:
        logger.debug(slots_dict_d1)

    else:
        slots_dict = slots_dict_d1
        return slots_dict
        

def exit_survey(event):
    userID = event.get('userId')
    intent = event['currentIntent']['name']
    fullfillment_state = 'Failed'
    message_content = "Your responses have been recorded. Please text 804.251.2876 with 'intake' to resume at any time"

    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fullfillment_state,
            'message': {'contentType': 'PlainText', 'content': message_content}
        }
        
    }
    
    logger.debug(response)
    return response


def validate_input(event):
    slots_dict = event['currentIntent']['slots']
    logger.debug(slots_dict)
    
    try:
        check_session(event)
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
    
    except ValueError:
        logger.debug(slotSessionAttributes)

    else:
        return input_response(slots_dict)
    return input_response(slots_dict)

