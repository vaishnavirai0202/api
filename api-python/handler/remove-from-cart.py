import json
import boto3
from pydantic import BaseModel, validator
from typing import Optional

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table('Carts')
users_table = dynamodb.Table('Users')
products_table = dynamodb.Table('Product')

# Pydantic model for validating cart item data
class CartItem(BaseModel):
    userId: str
    productId: str
    quantity: Optional[int] = 1  # Default quantity to 1 if not provided

    # Validation for quantity
    @validator('quantity', pre=True, always=True)
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

# Helper function to get an item from DynamoDB
def get_item(table, key):
    try:
        response = table.get_item(Key=key)
        return response.get('Item')
    except Exception as e:
        print(f"Error getting item: {e}")
        return None

# Helper function to delete an item from DynamoDB
def delete_item(table, key):
    try:
        table.delete_item(Key=key)
        return True
    except Exception as e:
        print(f"Error deleting item: {e}")
        return False

# Lambda handler function
def lambda_handler(event, context):
    try:
        # Parse the incoming request body to get user details and cart item data
        body = json.loads(event['body'])
        userId = body.get('userId')
        productId = body.get('productId')
        quantity = body.get('quantity', 1)  # Default to 1 if not provided

        # Validate the input data using Pydantic
        try:
            validated_item = CartItem(userId=userId, productId=productId, quantity=quantity)
        except ValueError as e:
            # If validation fails, return a 400 status code with detailed validation errors
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid input data',
                    'details': str(e)  # Validation error message
                }),
            }

        # Check if the user exists in the Users table using the get_item helper function
        user = get_item(users_table, {'userId': userId})
        if not user:
            # Return a 404 status code if the user is not found in the Users table
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'User with ID {userId} does not exist.'}),
            }

        # Check if the product exists in the Products table using the get_item helper function
        product = get_item(products_table, {'productId': productId})
        if not product:
            # Return a 404 status code if the product is not found in the Products table
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'Product with ID {productId} does not exist.'}),
            }

        # Define the key for deleting the cart item (based on userId and productId)
        key = {'userId': userId, 'productId': productId}

        # Call the delete_item helper function to remove the item from the Cart table
        result = delete_item(cart_table, key)

        if result:
            # Return a success response with a 200 status code if the product is removed from the cart
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Product removed from cart successfully'}),
            }
        else:
            # If deleting the item fails, return a 500 status code with an error message
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Failed to remove product from cart'}),
            }

    except Exception as e:
        # Log the error encountered during the process
        print(f"Error removing product from cart: {e}")

        # Handle DynamoDB-specific error when the item does not exist
        if 'ConditionalCheckFailedException' in str(e):
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'The specified user or product does not exist in the cart'
                }),
            }

        # Handle any other unexpected errors and return a generic error message
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error removing product from cart',
                'error': str(e)  # Include the error message from the exception
            }),
        }
