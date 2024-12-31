import json
import boto3

# Initialize DynamoDB resource
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
        # Fetch the order from the 'Orders' table
        response = orders_table.get_item(Key={'orderId': order_id})
        
        # If no order is found, return a 404 (Not Found) response
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No order found'})
            }

        # Return the order with a 200 (OK) status code
        order = response['Item']
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
