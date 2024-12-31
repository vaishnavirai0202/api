import json
import boto3
from pydantic import BaseModel, ValidationError, condecimal, validator
from typing import Optional
from helper.db_helper import query_products  # Import query_products
from helper.validation import validate_query_params  # Import QuerySchema and validate_query_params

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('Product')

# Lambda handler function
def lambda_handler(event, context):
    try:
        # Extract query parameters from the event object
        query_string_params = event.get('queryStringParameters', {})
        
        # Construct the queryParams object using the extracted query parameters
        query_params = {
            'keywords': query_string_params.get('keywords'),
            'category': query_string_params.get('category'),
            'subcategory': query_string_params.get('subcategory'),
            'minPrice': query_string_params.get('minPrice', type=float),
            'maxPrice': query_string_params.get('maxPrice', type=float),
        }

        # Validate the query parameters using Pydantic
        try:
            validated_params = validate_query_params(query_params)  # Validate and parse the query parameters
        except ValidationError as e:
            # If validation fails, return a 400 (Bad Request) response
            return {
                'statusCode': 400,  # Return 400 status code indicating bad request
                'body': json.dumps({
                    'message': 'Invalid query parameters',  # Message indicating invalid query parameters
                    'details': e.errors(),  # Return the validation error details for debugging
                }),
            }

        # If parameters are valid, query the database using the queryProducts function
        products = query_products(query_params)

        # Return the products in the response with a 200 (OK) status
        return {
            'statusCode': 200,  # Return 200 status code for successful operation
            'body': json.dumps({
                'products': products,  # Return the list of products found based on the query parameters
            }),
        }

    except Exception as error:
        # Log the error and return a 500 (Internal Server Error) response
        print(f"Error in handler: {error}")
        return {
            'statusCode': 500,  # Internal Server Error
            'body': json.dumps({'message': 'Internal server error'})  # Error message
        }
