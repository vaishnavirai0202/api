import json
import boto3
from pydantic import ValidationError
from helper.db_helper import save_item
from helper.validation import validate_user

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

# Lambda function handler
def lambda_handler(event, context):
    try:
        # Check if the request body exists
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Body is required'})
            }

        # Parse the request body
        body = json.loads(event['body'])

        # Validate the user data using Pydantic
        try:
            user = validate_user(body)  # This will raise an exception if validation fails
        except ValidationError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Validation failed', 'details': str(e)})
            }

        # Prepare the item to save in DynamoDB
        item = {
            'userId': user.email,  # Using email as the unique identifier
            'name': user.name,
            'email': user.email,
            'password': user.password,  # In production, ensure passwords are hashed
            'shippingAddress': user.shippingAddress
        }

        # Save the validated user data to DynamoDB
        result = save_item(item, 'Users')  # Call the save_item function to save the item in DynamoDB

        if result:
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'User registered successfully'})
            }

        # If saving fails
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed to register user'})
        }

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error: {e}")

        # Return an internal server error if something goes wrong
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
