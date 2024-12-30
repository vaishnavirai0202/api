import json
import boto3
from pydantic import BaseModel, Field, validator
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

# Helper function to save an item to DynamoDB
def save_item(item, table):
    try:
        table.put_item(Item=item)
        return True
    except Exception as e:
        print(f"Error saving item: {e}")
        return False

# Lambda handler function
def lambda_handler(event, context):
    try:
        # Parse the request body to extract userId, productId, and quantity
        body = json.loads(event['body'])
        userId = body.get('userId')
        productId = body.get('productId')
        quantity = body.get('quantity', 1)

        # Validate the input data using Pydantic
        try:
            validated_item = CartItem(userId=userId, productId=productId, quantity=quantity)
        except ValueError as e:
            # If validation fails, return a 400 status code with detailed validation errors
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid input data',
                    'details': str(e)  # Detailed validation errors
                }),
            }

        # Check if the user exists in the Users table using the get_item helper function
        user = get_item(users_table, {'userId': userId})
        if not user:
            # If the user does not exist, return a 404 status code
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'User with ID {userId} does not exist.'}),
            }

        # Check if the product exists in the Products table using the get_item helper function
        product = get_item(products_table, {'productId': productId})
        if not product:
            # If the product does not exist, return a 404 status code
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'Product with ID {productId} does not exist.'}),
            }

        # Create a cartItem object with the userId, productId, and quantity
        cart_item = {
            'userId': userId,
            'productId': productId,
            'quantity': quantity
        }

        # Insert the cart item into the Cart table using the save_item helper function
        result = save_item(cart_item, cart_table)

        if result:
            # Return a success response with a 201 status code if the product is added to the cart
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Product added to cart successfully'}),
            }
        else:
            # If saving the item fails, return a 500 status code with a failure message
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Failed to add product to cart'}),
            }

    except Exception as e:
        # Log any errors that occur during the process for debugging purposes
        print(f"Error: {e}")

        # Return a 500 status code with a generic error message in case of internal server error
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'}),
        }
