# Import necessary modules and functions
import json
import boto3
from helper.validation import validate_product  # Import ProductSchema and validate_product
from helper.db_helper import save_item  # Assuming save_item is in another helper file
from decimal import Decimal
from pydantic import ValidationError

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('Product')

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

        # Validate the product data using the validate_product function
        try:
            product = validate_product(body)  # Validate and parse the incoming data into ProductSchema model
        except ValidationError as e:
            # If validation fails, return a 400 Bad Request response with error details
            return {
                'statusCode': 400,
                'body': json.dumps({'message': e.errors()[0]['msg']})
            }

        # Construct the product item to be inserted into DynamoDB
        product_item = {
            'productId': product.productId,
            'name': product.name,
            'category': product.category or None,
            'subcategory': product.subcategory or None,
            'price': Decimal(str(product.price)),  # Use Decimal for precise floating point handling
            'keywords': product.keywords,
        }

        # Save the product item to DynamoDB using the imported save_item function
        result = save_item(product_item, products_table)

        if result:
            # Return a 201 Created response if the product was successfully saved
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Product created successfully', 'product': product_item})
            }

        # If saving the product fails, return a 500 Internal Server Error response
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed to create product'})
        }

    except Exception as e:
        # Log and return a 500 Internal Server Error if an unexpected error occurs
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
