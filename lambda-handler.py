import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

global slots_current


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


def input_response(slots_lex):
    response = {
        'dialogAction': {
            'type': "Delegate",
            'slots': slots_lex
        }
    }
    return response


def fulfillment_response(session_attributes, fullfillment_state, message):
    filled_response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': "Close",
            'fulfillmentState': fullfillment_state,
            'message': message + '. Survey is now complete. Clinician will review responses and send gift card to '
                                 'number on file'
        }
    }
    return filled_response


def merge_slots(dict1, dict2):
    d1 = dict1['Slots']
    d2 = dict2['Slots']
    d1.update(d2)
    res = {'Slots': d1}
    return res


def validate_input(event):
    try:
        slots_current_all = event['currentIntent']['slots']
        slots_current_no_nulls = list({ele for ele in slots_current_all if slots_current_all[ele]})
        
        if slots_current_no_nulls['raceOne'] != '4':
            slots_1 = {
                'Slots': {
                    'raceTwo': '8',
                    'raceThree': '12'
                }
            }
            slots_lex = merge_slots(slots_1, slots_current_no_nulls)
            return input_response(slots_lex)

        elif slots_current_no_nulls['raceOne'] == '1':
            slots_2 = {
                'Slots': {
                    'milStatus': '1',
                    'milService': '5',
                    'milDeployment': '1'
                }
            }
            slots_lex = merge_slots(slots_2, slots_current_no_nulls)
            return input_response(slots_lex)

        elif slots_current_no_nulls['activitySexOne'] == '1':
            slots_3 = {
                'Slots': {
                    'activitySexTwo': '1',
                    'activitySexThree': '0',
                    'activitySexFour': '0',
                    'activitySexFive': '0',
                    'activitySexSix': '1'
                }
            }
            slots_lex = merge_slots(slots_3, slots_current_no_nulls)
            return input_response(slots_lex)

        else:
            raise ValueError('No Data Validation Conditions Met')
    except ValueError:
        slots_lex = slots_current_no_nulls
        return input_response(slots_lex)


def complete_survey(event):
    userID = event.get('userId')
    intent = event['intentName']
    sessionID = event.get('sessionId')
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

    return fulfillment_response(fullfillment_state, message)
