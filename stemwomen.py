"""
This is the logic for the STEM Skill
"""

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from random import randint


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "STEM Women - " + title,
            'content': "STEM Women - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome, to STEM Women. " \
                    " Science, technology, engineering, and math, which are STEM fields, are predominantly male." \
                    " STEM Women seeks to close the gender gap by highlighting women doing great things in STEM. " \
                    " Hear about an amazing woman from any STEM field by saying, tell me about a woman in science or tell me about a woman in technology. You can even say, tell me about a woman in STEM."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "STEM stands for Science, Technology, Engineering, and Math. " \
                    " Hear about an amazing woman in STEM by saying, tell me about a woman in engineering or tell me about a woman in math. You can even say, tell me about a woman in STEM."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for advocating for women in stem by using STEM Women. " \
                    "Know a woman that should be showcased? Email keysha at s 4 technology dot com"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def query_random_woman():
    table = boto3.resource('dynamodb').Table('COLORS_STEM')

    # dynamo is case-sensitive
    try:
        response = table.scan(
            Limit=1000)
        print("response returned from the database")
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if response['Count'] > 0:
            print('size > 0')
            random_num = randint(0, response['Count'] - 1)
            print(random_num)
            print(response['Items'][random_num]['first_name'])
            return response['Items'][random_num]['first_name'] + " " + response['Items'][random_num][
                'last_name'] + " is a " + response['Items'][random_num]['title'] + ". She works as, " + \
                   response['Items'][random_num]['abstract'] + "."

    return "A woman in that field hasn't been added yet. Please check back again soon as we add STEM women on a daily basis."


def query_single_person_by_field(field):
    print(field)
    # Note: role used for executing this Lambda function should have read access to the table.
    table = boto3.resource('dynamodb').Table('COLORS_STEM')

    # dynamo is case-sensitive
    try:
        response = table.scan(
            FilterExpression=Attr('field').eq(field.lower()),
            Limit=1000)
        print("response returned from the database")
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if response['Count'] > 0:
            print('size > 0')
            random_num = randint(0, response['Count'] - 1)
            print(random_num)
            print(response['Items'][random_num]['first_name'])
            return response['Items'][random_num]['first_name'] + " " + response['Items'][random_num][
                'last_name'] + " is a " + response['Items'][random_num]['title'] + ". She works as, " + \
                   response['Items'][random_num]['abstract'] + "."
    return "A woman in that field hasn't been added yet. Please check back again soon as we add STEM women on a daily basis."


# retrieves a person by field
def get_role_model_intent(intent, userid):
    print("get_role_model_intent")
    print(intent)
    stem_list = ['science', 'technology', 'engineering', 'math']
    session_attributes = {}
    should_end_session = True
    card_title = "Search for a woman in STEM"
    reprompt_text = "Do you want to hear another?"

    if 'value' in intent['slots']['Field']:
        # query the database for field only
        field = intent['slots']['Field']['value']

        if field.lower() == 'tech':
            field = 'technology'

        if field.lower() == 'mathematics':
            field = 'math'

        if field.lower() in stem_list:
            speech_output = query_single_person_by_field(field)
        else:
            speech_output = query_random_woman()
        print('query the database for field')
        print(speech_output)
    else:
        # query for a random woman
        speech_output = query_random_woman()

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print(intent)
    print(intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "GetWomanIntent":
        return get_role_model_intent(intent, session['user']['userId'])
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.xxxxxxxxxxxxxxx"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
