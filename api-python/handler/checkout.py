import json
import uuid
import boto3
from datetime import datetime
from helper.db_helper import get_item, save_item  # Importing helper functions

# Initialize DynamoDB resource (This is optional, as it is done inside the helper file)
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table('Product_table')
orders_table = dynamodb.Table('Order_table')

# Lambda handler function
def lambda_handler(event, context):
    try:
        # Parse the incoming request body to get user details and cart items
        body = json.loads(event['body'])
        userId = body.get('userId')
        shippingAddress = body.get('shippingAddress')
        paymentMethod = body.get('paymentMethod')
        cartItems = body.get('cartItems')

        # Validate if all required fields are present
        if not userId or not shippingAddress or not paymentMethod or not cartItems or len(cartItems) == 0:
            return {
                'statusCode': 400,  # Return 400 if required fields are missing or cartItems is empty
                'body': json.dumps({'message': 'UserID, ShippingAddress, PaymentMethod, and CartItems are required'})
            }

        totalAmount = 0  # Initialize totalAmount to 0 for calculating total order price

        # Iterate through each item in the cart to calculate the total amount
        for item in cartItems:
            productId = item.get('productId')
            key = {'productId': productId}  # Prepare the product key using productId from cart item

            # Fetch product data from the 'Products' table
            product = get_item('Product_table', key)

            # If product is not found in the database, return a 404 error
            if not product:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': f'Product {productId} not found'})
                }

            # Calculate the total amount by multiplying product price and quantity
            totalAmount += product['price'] * item['quantity']

        # Generate a unique order ID using UUID
        orderId = f"order-{uuid.uuid4()}"

        # Create the orderDetails object with the information for the new order
        order_details = {
            'orderId': orderId,  # Unique order ID
            'userId': userId,  # User ID placing the order
            'shippingAddress': shippingAddress,  # Shipping address for the order
            'paymentMethod': paymentMethod,  # Payment method selected by the user
            'cartItems': cartItems,  # Items included in the cart
            'orderStatus': 'Placed',  # Initial status of the order
            'orderDate': datetime.utcnow().isoformat(),  # Current date and time in ISO format
            'totalAmount': totalAmount  # Total calculated amount for the order
        }

        # Save the order details to the 'Orders' table using the save_item helper function
        save_order_result = save_item(order_details, 'Order_table')

        if save_order_result:
            return {
                'statusCode': 201,  # Success status code
                'body': json.dumps({'message': 'Order placed successfully', 'orderId': orderId}),
            }
        else:
            # If saving the order failed, return a 500 Internal Server Error response
            return {
                'statusCode': 500,  # Internal server error status code
                'body': json.dumps({'message': 'Failed to save order details.'}),
            }

    except Exception as error:
        # Log any errors that occur during processing
        print(f"Error: {error}")

        # Return a 500 Internal Server Error response for any exceptions that occur
        return {
            'statusCode': 500,  # Internal server error status code
            'body': json.dumps({'message': 'Internal server error'}),
        }
