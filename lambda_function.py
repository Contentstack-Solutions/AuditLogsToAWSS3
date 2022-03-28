import os
import json
import datetime
import requests
import boto3
'''
Gets Audit logs - Since yesterday (Today minus one day), saves to JSON (<date>.json) and finally uploads to the designated S3 bucket
2022-03-15
oskar.eiriksson@contentstack.com

Environmental Variables Needed:
- CS_REGION - Either NA or EU - If nothing is defined, it defaults to NA (North America)
- CS_STACKS - One or more stacks to save the audit logs from. On the format: <API_KEY1>,<MANAGEMENT_TOKEN1>;<API_KEY2>,<MANAGEMENT_TOKEN2>;etc...
- S3_BUCKET - Name of the bucket the logs will be uplodaded to. Make sure the Lambda function has access to write to the bucket via an IAM role.
'''

stacks = os.getenv('CS_STACKS', '').split(';') # String with API keys and Management Tokens
bucket = os.getenv('S3_BUCKET', None) # Name of the S3 bucket

def getRequestHeader(apiKey, managementToken):
    '''
    Creating an access header for all different stacks
    '''
    return {
        'authorization': managementToken,
        'api_key': apiKey,
        'Content-Type': 'application/json'
        }

regionMap = {
    'NA': 'https://api.contentstack.io/',
    'na': 'https://api.contentstack.io/',
    'EU': 'https://eu-api.contentstack.com/',
    'eu': 'https://eu-api.contentstack.com/'
}

region = regionMap[os.getenv('CS_REGION', 'NA')] # Defaulting to the North America Region


def getAuditLogs(yesterday, today, apiKey=None, managementToken=None):
    '''
    Get Audit Logs - If timestamp: then only logs since then and newer 
    sample url: https://{{base_url}}/v3/audit-logs?include_count=true&query={ "created_at": { "$gte": "2022-02-19T00:00:00.000Z" } }
    '''
    url = '{region}v3/audit-logs?audit-logs?include_count=true'.format(region=region)
    # Query to Contentstack Nothing older than yesterday (gte = greater or equal) and nothing from today or newer (lt = less than)
    query = '&query={"$and":[{ "created_at": { "$gte": "' + yesterday + '" } },{ "created_at": { "$lt": "' + today + '" } }]}'
    url = url + query
    res = requests.get(url, headers=getRequestHeader(apiKey, managementToken))
    if res.status_code in (200, 201):
        return res.json()
    return returnStatement(res.status_code, res.text)

def returnStatement(statusCode=200, msg='OK'):
    '''
    Return Statement
    '''
    return {
        'statusCode': statusCode,
        'body': json.dumps(msg)
    }

def uploadToS3(localFile, s3File):
    s3 = boto3.client('s3')
    try:
        upload = s3.upload_file(localFile, bucket, s3File)
        print(upload)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return None
    except:
        print("Something wrong. Possibly missing credentials.")
        return None

def lambda_handler(event, context):
    if not stacks or not bucket:
        return returnStatement(400, 'No stacks or bucket defined as an env variable.')
    # Get yesterdays date on the right format for the query - and to use in the filename
    yesterdayFilename = str(datetime.date.today() - datetime.timedelta(days=1))
    yesterday = yesterdayFilename + 'T00:00:00.000Z'
    today = str(datetime.date.today()) + 'T00:00:00.000Z'
    for stack in stacks:
        stack = stack.split(',') # Splitting up a single stack env var into api key and token
        stackAuditLogs = getAuditLogs(yesterday, today, stack[0], stack[1]) # Fetching Audit logs from Contentstack
        if 'logs' in stackAuditLogs: # If 'logs' key in response -> We have logs
            filename = '{yesterdayFilename}_{stack}.json'.format(yesterdayFilename=yesterdayFilename, stack=stack[0])
            print('Logs found for stack {}. Uploading them to S3.'.format(stack[0]))
            # Writing dictionary logs to JSON file
            with open('/tmp/{}'.format(filename), 'w') as outfile: # Writing logs to a tmp file
                json.dump(stackAuditLogs, outfile, indent=4)         
            # Uploading the JSON log file to S3 bucket
            uploadToS3('/tmp/{}'.format(filename), filename)            
        else:
            print('No logs found for stack {}'.format[stack[0]])
            print(stackAuditLogs)
    
    return returnStatement()
