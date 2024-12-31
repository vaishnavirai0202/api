import json
from helper.db_helper import get_item  # Import the helper function

def lambda_handler(event, context):
    # Extract the userId from the query string parameters in the event
    user_id = event.get('queryStringParameters', {}).get('userId')
    print(user_id)  # Logging the userId for debugging

    # If userId is not provided, return a 400 (Bad Request) response
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'User ID is required'})
        }

    # Construct the key to query the 'Users' table by userId
    key = {'userId': user_id}

    try:
        # Fetch the user profile using the get_item helper function
        user_profile = get_item('Users', key)
        
        # If no user profile is found, return a 404 (Not Found) response
        if not user_profile:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'User not found'})
            }
        
        # Return the user profile with a 200 (OK) status code if the user is found
        return {
            'statusCode': 200,
            'body': json.dumps(user_profile)  # Return the user profile details
        }

    except Exception as error:
        # Log any errors encountered
        print(f"Error fetching user profile: {error}")
        
        # Return a 500 (Internal Server Error) if there was an exception during the process
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
