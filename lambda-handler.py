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


def input_response(session_attributes, slots):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': "Delegate",
            'slots': slots
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


def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res


def validate_input(event):
    userID = event.get('userId')
    intent = event['currentIntent']['name']
    slots_current = event['currentIntent']['slots']
    session_attributes = event.get('sessionAttributes')
    bot_message = event.get['botRequest']
    user_input = event.get['inputTranscript']

    try:
        if bot_message == 'On scale 5 - 8, What ethnic group do you consider yourself? 5-Mexican, 6-Puerto Rican, ' \
                          '7-South American, 8-None of these' and user_input != '4':
            slots_1 = {
                'Slots': {
                    'raceTwo': '8',
                    'raceThree': '12'
                }
            }
            slots = merge_dicts(slots_1, slots_current)
            return input_response(session_attributes, slots)

        elif bot_message == 'Are you currently on active duty? 1-No 2-Yes, Armed Forces 3-Yes, Reservist 4-Yes, ' \
                            'National Guard' and user_input == '1':
            slots_2 = {
                'Slots': {
                    'milStatus': '1',
                    'milService': '5',
                    'milDeployment': '1'
                }
            }
            slots = merge_dicts(slots_2, slots_current)
            return input_response(session_attributes, slots)

        elif bot_message == 'If you had sexual activity in the last 30 days, which type of sexual contact was ' \
                            'involved? 1-Not applicable to me 2-vaginal 3-oral 4-anal' and user_input == '1':
            slots_3 = {
                'Slots': {
                    'activitySexTwo': '1',
                    'activitySexThree': '0',
                    'activitySexFour': '0',
                    'activitySexFive': '0',
                    'activitySexSix': '1'
                }
            }
            slots = merge_dicts(slots_3, slots_current)
            return input_response(session_attributes, slots)

        else:
            raise ValueError('No Data Validation Conditions Met')
    except ValueError:
        slots = slots_current
        return input_response(session_attributes, slots)


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

    fulfillment_response(fullfillment_state, message)
