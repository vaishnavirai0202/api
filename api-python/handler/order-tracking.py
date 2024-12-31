import json
import boto3
from helper.db_helper import query_order_track  # Import the get_item function from dynamodb_helpers.py

# Initialize DynamoDB resource (optional, as it's initialized in the helper file)
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('Order_table')  # The name of the 'Orders' table

def lambda_handler(event, context):
    # Extract the orderId from the query string parameters in the event
    order_id = event.get('queryStringParameters', {}).get('orderId')

    # Validate that orderId is provided
    if not order_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Order ID is required'})
        }
    
    try:
        # Fetch the order from the 'Orders' table using the get_item function
        order = query_order_track('Order_table', {'orderId': order_id})
        
        # If no order is found, return a 404 (Not Found) response
        if not order:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No order found'})
            }

        # Return the order with a 200 (OK) status code
        return {
            'statusCode': 200,
            'body': json.dumps(order)  # Return the order details
        }

    except Exception as error:
        # Log any errors encountered
        print(f"Error fetching order details: {error}")
        
        # Return a 500 (Internal Server Error) if something went wrong
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
