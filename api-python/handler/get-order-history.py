import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('Orders')  # The table where order details are stored

# Helper function to query orders from the Orders table
def query_order(user_id, table):
    try:
        # Query the Orders table to fetch orders for the given user_id
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id)
        )
        return response.get('Items', [])  # Return order items if found
    except Exception as e:
        print(f"Error querying orders: {e}")
        return None

# Lambda handler function
def lambda_handler(event, context):
    # Extract the userId from the query parameters
    user_id = event.get('queryStringParameters', {}).get('userId')

    # Validate that the userId is provided
    if not user_id:
        return {
            'statusCode': 400,  # Return 400 if userId is not provided
            'body': json.dumps({'message': 'User ID is required'})  # Include a message indicating userId is missing
        }
    
    try:
        # Fetch the user's order history using the helper function
        order_history = query_order(user_id, orders_table)

        # If no order history is found, return a 404 response
        if not order_history:
            return {
                'statusCode': 404,  # Return 404 if no orders are found for the user
                'body': json.dumps({'message': 'User not found'})  # Provide a message indicating no user found
            }

        # Return the order history if found
        return {
            'statusCode': 200,  # Return 200 for successful retrieval of order history
            'body': json.dumps(order_history)  # Include the order history data in the response body
        }
    except Exception as error:
        # Log any errors encountered during the process
        print(f"Error fetching user profile: {error}")
        
        # Return a 500 response if there is an error fetching the order history
        return {
            'statusCode': 500,  # Internal server error status code
            'body': json.dumps({'message': 'Internal server error'})  # General error message
        }
