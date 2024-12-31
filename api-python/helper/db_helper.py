import boto3
from botocore.exceptions import ClientError

# Instantiate a DynamoDB client
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

# Function to save an item to DynamoDB
def save_item(item, table_name):
    table = dynamodb.Table(table_name)
    try:
        table.put_item(Item=item)  # Save item to DynamoDB
        return True
    except ClientError as error:
        print(f"Error: {error}")
        return False

# Function to get an item from DynamoDB
def get_item(table_name, key):
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key=key)
        return response.get('Item')  # Return the item if found, otherwise None
    except ClientError as error:
        print(f"Error: {error}")
        raise Exception("Failed to fetch data from DynamoDB")

# Function to query orders by user ID
def query_orders(user_id, table_name):
    table = dynamodb.Table(table_name)
    try:
        response = table.query(
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={':userId': user_id}
        )
        return response.get('Items', [])  # Return list of orders, empty if none found
    except ClientError as error:
        print(f"Error fetching orders: {error}")
        raise Exception("Failed to fetch orders from DynamoDB")

# Function to query orders by order ID (with a Global Secondary Index)
def query_order_track(order_id, table_name):
    table = dynamodb.Table(table_name)
    try:
        response = table.query(
            IndexName='OrderIndex',  # Assuming OrderIndex exists
            KeyConditionExpression='orderId = :orderId',
            ExpressionAttributeValues={':orderId': order_id}
        )
        return response.get('Items', [])  # Return list of orders, empty if none found
    except ClientError as error:
        print(f"Error fetching orders: {error}")
        raise Exception("Failed to fetch orders from DynamoDB")

# Function to delete an item from DynamoDB
def delete_item(table_name, key):
    table = dynamodb.Table(table_name)
    try:
        table.delete_item(Key=key)
        return True
    except ClientError as error:
        print(f"Error deleting item: {error}")
        raise error

# Function to update an item in DynamoDB
def update_item(table_name, key, update_expression_parts, expression_attribute_values, expression_attribute_names):
    table = dynamodb.Table(table_name)
    update_expression = 'SET ' + ', '.join(update_expression_parts)
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        return response.get('Attributes')  # Return the updated attributes
    except ClientError as error:
        print(f"Error updating item: {error}")
        raise error

# Function to query products based on various parameters like keywords, category, price range, etc.
def query_products(params):
    table = dynamodb.Table('Product')
    query_params = {
        'KeyConditionExpression': 'keywords = :keywords',
        'ExpressionAttributeValues': {':keywords': params['keywords']},
        'FilterExpression': ''
    }
    
    if 'category' in params:
        query_params['FilterExpression'] += 'category = :category'
        query_params['ExpressionAttributeValues'][':category'] = params['category']
    
    if 'subcategory' in params:
        query_params['FilterExpression'] += ' AND subcategory = :subcategory' if query_params['FilterExpression'] else 'subcategory = :subcategory'
        query_params['ExpressionAttributeValues'][':subcategory'] = params['subcategory']
    
    if 'minPrice' in params or 'maxPrice' in params:
        price_filter = 'price BETWEEN :minPrice AND :maxPrice'
        query_params['FilterExpression'] += ' AND ' + price_filter if query_params['FilterExpression'] else price_filter
        query_params['ExpressionAttributeValues'][':minPrice'] = params.get('minPrice', 0)
        query_params['ExpressionAttributeValues'][':maxPrice'] = params.get('maxPrice', 999999)
    
    try:
        response = table.query(**query_params)
        return response.get('Items', [])  # Return matching items
    except ClientError as error:
        print(f"Error querying products: {error}")
        raise error
