import json
import boto3
from pydantic import BaseModel, EmailStr, ValidationError
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

# Define the user model for validation using Pydantic
class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    shippingAddress: str

# Helper function to save user data to DynamoDB
def save_item(user):
    try:
        response = table.put_item(
            Item={
                'userId': user.email,  # Using email as the unique identifier
                'name': user.name,
                'email': user.email,
                'password': user.password,  # In production, ensure passwords are hashed
                'shippingAddress': user.shippingAddress
            }
        )
        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False
    except ClientError as e:
        print(f"Error saving user: {e}")
        return False

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
            user = User(**body)  # This will raise an exception if validation fails
        except ValidationError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': str(e)})
            }

        # Save the validated user data to DynamoDB
        result = save_item(user)

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
