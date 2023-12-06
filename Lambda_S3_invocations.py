import boto3
import pandas as pd
from io import BytesIO
import urllib.parse

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get the S3 bucket and object key from the event
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # To Excel file from S3
    try: 
        response = s3.get_object(Bucket=input_bucket, Key=input_key)
        excel_data = response['Body'].read()

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(input_key, input_bucket))
        raise e
    # Convert the Excel data to a DataFrame
    df = pd.read_excel(BytesIO(excel_data))

    # Change the column named from 'TransactionAmount' to the name of column you want 
    if 'TransactionAmount' not in df.columns:
        raise ValueError("The Excel file must have a column named 'TransactionAmount'.")

    # Sort the DataFrame by transaction amount in descending order
    df_sorted = df.sort_values(by='TransactionAmount', ascending=False)

    # Get the top 10 rows with the maximum transaction amounts you can increase the number of rows you want
    top_10_transactions = df_sorted.head(10)

    # Convert the result DataFrame to Excel
    output_excel_data = top_10_transactions.to_excel(index=False)

    # Upload the result to the output S3 bucket with the same key as the input
    s3.put_object(Bucket=input_bucket, Key=input_key, Body=output_excel_data)

    return {
        'statusCode': 200,
        'body': 'Analysis completed and result uploaded to S3.'
    }
