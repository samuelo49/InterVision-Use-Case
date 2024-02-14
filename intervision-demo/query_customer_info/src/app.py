import os
import json
import boto3

# Access the DynamoDB table name from environment variables
table_name = os.environ['CUSTOMER_INFO_TABLE_NAME']

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    print(f'Event: {json.dumps(event)}')
    # Extract caller's phoneNumber from the event object passed by Amazon Connect
    customer_phone = event.get('Details', {}).get('ContactData', {}).get('CustomerEndpoint', {}).get('Address', '')

    customer_name = 'Jane Smith'

    response = {}
    if customer_phone:
        # Query DynamoDB for the customer based on the phoneNumber
        try:
            response = table.get_item(Key={'CustomerID': customer_phone})
        except Exception as e:
            print(f"Error querying DynamoDB: {str(e)}")
            return {
                'CustomerFound': False,
                'Error': 'Failed to query customer information'
            }

    customer_info = response.get('Item')

    if customer_info:
        # Format the response for an existing customer
        return format_existing_customer_response(customer_info)
    else:
        # Handle new customer
        new_customer_info = handle_new_customer(customer_phone, customer_name=customer_name)
        return format_new_customer_response(new_customer_info)


def format_existing_customer_response(customer_info):
    """Formats the response for an existing customer."""
    past_issues_count = len(customer_info.get('PastIssues', []))
    last_sales_rep = customer_info.get('SalesRep', {}).get('Name', 'N/A')

    return {
        'CustomerName': 'John Doe',
        'CustomerFound': True,
        'CustomerStatus': customer_info.get('CustomerStatus', 'Unknown'),
        'PastIssuesCount': past_issues_count,
        'LastSalesRep': last_sales_rep
    }


def handle_new_customer(customer_phone, customer_name):
    """Inserts a new customer into DynamoDB and returns their info."""
    new_customer_info = {
        'CustomerID': customer_phone,
        'CustomerName': customer_name,
        'CustomerStatus': 'New',
        'PastIssues': [],
        'SalesRep': {},
        'CustomerReps': []
    }
    try:
        table.put_item(Item=new_customer_info)
    except Exception as e:
        print(f"Error inserting new customer to DynamoDB: {str(e)}")
    return new_customer_info


def format_new_customer_response(new_customer_info):
    """Formats the response for a new customer."""
    return {
        'CustomerFound': False,
        'CustomerStatus': new_customer_info.get('CustomerStatus', 'New'),
        'PastIssuesCount': 0,
        'LastSalesRep': 'N/A'
    }
