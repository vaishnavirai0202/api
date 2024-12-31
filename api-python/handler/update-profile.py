import json
import boto3
from helper.db_helper import update_item  # Import the update_item function
from helper.validation import validate_cart_item  # Import CartItem class and validate_cart_item function

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('User_table')  # Table name for Users

def lambda_handler(event, context):
    try:
        # Parse the incoming request body
        body = json.loads(event['body'])

        # Extract user details from the request body
        user_id = body.get('userId')
        updated_name = body.get('updatedName')
        updated_email = body.get('updatedEmail')
        updated_shipping_address = body.get('updatedShippingAddress')

        # Validate that userId is provided
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'User ID is required'})
            }

        # Initialize parts for the update expression, attribute values, and attribute names
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}

        # Construct the update expression dynamically based on provided fields
        if updated_name:
            update_expression_parts.append('#name = :name')
            expression_attribute_values[':name'] = updated_name
            expression_attribute_names['#name'] = 'name'

        if updated_email:
            update_expression_parts.append('#email = :email')
            expression_attribute_values[':email'] = updated_email
            expression_attribute_names['#email'] = 'email'

        if updated_shipping_address:
            update_expression_parts.append('#shippingAddress = :shippingAddress')
            expression_attribute_values[':shippingAddress'] = updated_shipping_address
            expression_attribute_names['#shippingAddress'] = 'shippingAddress'

        # If no fields are provided for updating, return a 400 status code
        if not update_expression_parts:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No fields to update'})
            }

        # Construct the update expression by joining the parts
        update_expression = 'SET ' + ', '.join(update_expression_parts)

        # Update the user profile in DynamoDB using the helper function
        response = update_item(
            'User_table',  # Table name
            {'userId': user_id},  # Key to identify the item
            update_expression_parts,
            expression_attribute_values,
            expression_attribute_names
        )

        # Extract updated attributes from the response
        updated_attributes = response or {}

        # Return a success response with the updated attributes
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User profile updated successfully',
                'updatedAttributes': updated_attributes
            })
        }

    except Exception as error:
        # Log the error and return a 500 status code in case of failure
        print(f"Error updating profile: {error}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error updating profile',
                'error': str(error)
            })
        }
