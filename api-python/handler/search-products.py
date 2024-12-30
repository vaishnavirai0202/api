import json
import boto3
from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('Product')

# Pydantic model for validating query parameters
class QueryParams(BaseModel):
    keywords: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    minPrice: Optional[float] = None
    maxPrice: Optional[float] = None

    # Validate price range
    @validator('minPrice', 'maxPrice', pre=True, always=True)
    def validate_price_range(cls, v, values, field):
        if field.name == 'minPrice' and v is not None and values.get('maxPrice') is not None and v > values['maxPrice']:
            raise ValueError("minPrice cannot be greater than maxPrice")
        if field.name == 'maxPrice' and v is not None and values.get('minPrice') is not None and v < values['minPrice']:
            raise ValueError("maxPrice cannot be less than minPrice")
        return v

# Helper function to query the products from DynamoDB
def query_products(query_params: dict):
    try:
        # Construct the DynamoDB query parameters
        key_condition_expression = 'keywords = :keywords'
        expression_attribute_values = {
            ':keywords': query_params['keywords'],
        }

        # Optionally add filters for category, subcategory, and price range
        if query_params.get('category'):
            key_condition_expression += ' AND category = :category'
            expression_attribute_values[':category'] = query_params['category']
        if query_params.get('subcategory'):
            key_condition_expression += ' AND subcategory = :subcategory'
            expression_attribute_values[':subcategory'] = query_params['subcategory']
        if query_params.get('minPrice') or query_params.get('maxPrice'):
            filter_expression = 'price BETWEEN :minPrice AND :maxPrice' if query_params.get('minPrice') and query_params.get('maxPrice') else None
            if filter_expression:
                expression_attribute_values[':minPrice'] = query_params['minPrice']
                expression_attribute_values[':maxPrice'] = query_params['maxPrice']
            else:
                if query_params.get('minPrice'):
                    filter_expression = 'price >= :minPrice'
                    expression_attribute_values[':minPrice'] = query_params['minPrice']
                if query_params.get('maxPrice'):
                    filter_expression = 'price <= :maxPrice'
                    expression_attribute_values[':maxPrice'] = query_params['maxPrice']

        # Execute the query in DynamoDB
        response = products_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        return response['Items']  # Return the products found
    except Exception as e:
        print(f"Error querying products: {e}")
        raise Exception("Error querying products from DynamoDB")

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
            validated_params = QueryParams(**query_params)
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
