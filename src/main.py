from jsonschema import validate, ValidationError
from json_schema import post_body_schema
from client.hendrik.http_requests import AccountInfo, UserMatchData, Match, Player
import json
from typing import List, Tuple
from model.lambda_response import LambdaResponse
import logging as log

log.getLogger().setLevel(log.INFO)

def invalid_schema_response():
    error_body = {
        'error': 'Invalid post body'
    }
    return {
        'isBase64Encoded': False,
        'statusCode': 500,
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps(error_body)
    }

def error_schema_response(msg: str = None):
    error_body = {
        'error': msg
    }
    return {
        'isBase64Encoded': False,
        'statusCode': 204,
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps(error_body)
    }

def validate_post_body(event):
    try:
        schema = post_body_schema.schema
        validate(instance=event, schema=schema)
        return True
    except ValidationError:
        return False

def get_puuid(event):
    username = event['username']
    tag = event['tag']
    account = AccountInfo(username, tag)
    return account.get_puuid()

def find_matches_with_target_username(puuid: str, target_username: str) -> List[Tuple[Match, Player]]:
    user = UserMatchData(puuid)
    matches = user.matches
    result = []
    for match in matches:
        user = match.contains_user(target_username)
        if user:
            result.append((match, user))

    return result

def handler(event, lambda_context):
    log.info(f'Event is: {event}')
    post_request_body = json.loads(event['body'])
    # validate post body
    if not validate_post_body(post_request_body):
        return invalid_schema_response()

    # get current user's puuid
    puuid = get_puuid(post_request_body)
    target_username = post_request_body['target_username']
    if puuid is None:
        return error_schema_response('User not found')
    found_matches = find_matches_with_target_username(puuid, target_username)
    lambda_response = LambdaResponse(found_matches)
    return lambda_response.json()

if __name__ == '__main__':
    body = {
        'username': 'thisGuyCodes',
        'tag': '0991',
        'target_username': 'ElSeñorDeLaNoche'
    }
    string_body = json.dumps(body)
    event = {
        'body': string_body
    }
    response = handler(event, None)
    print(json.dumps(response))