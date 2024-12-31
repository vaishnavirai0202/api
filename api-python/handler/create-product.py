import json
import boto3
from pydantic import BaseModel, ValidationError, validator
from decimal import Decimal

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('Product_table')

# Pydantic model for product validation
class Product(BaseModel):
    productId: str
    name: str
    category: str = None
    subcategory: str = None
    price: float
    keywords: str
    
    # Optional validator for price to ensure it is a valid positive number
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0.")
        return v

# Helper function to save an item to DynamoDB
def save_item(item, table_name):
    try:
        # Save the item to the DynamoDB table
        response = products_table.put_item(Item=item)
        return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False
    except Exception as e:
        print(f"Error saving item to DynamoDB: {e}")
        return False

# Lambda handler function
def lambda_handler(event, context):
    try:
        # Parse the request body from the incoming event
        body = json.loads(event['body'])
        
        # Validate the product data using Pydantic
        try:
            product = Product(**body)  # Validate and parse the incoming data into Product model
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

        # Save the product item to DynamoDB
        result = save_item(product_item, 'Product')

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
