# AuditLogsToAWSS3
AWS Lambda function to backup Contentstack audit logs to an AWS S3 bucket - Using Python. Scheduled to run once a day. Supports one or more stacks using a Management Token.

## Step by Step
---
**1. Create a Lambda function**
* Upload lambda.zip to AWS Lambda - or create your own zip file and upload.
    * Upload a zip file with the lambda_function.py file and dependencies.
    * It's good to update both code and configuration in Lambda with `awscli`.
        * To update code via `awscli`:
            * install pip modules into a subdirectory like this:
            * `pip install --target ./package requests`.
        * Add all files and folders from the `package` folder (not the `package` folder itself) into a zip file with the `lambda_function.py` and upload to Lambda like this:
            * `aws lambda update-function-code --function-name ContentstackSlackPOC --zip-file fileb://function.zip`

**2. Create a S3 bucket**
* Remember not have it publicly accessible.

**3. Create an IAM Role for the Lambda function that has access to the S3 bucket.** 

(See: https://aws.amazon.com/premiumsupport/knowledge-center/lambda-execution-role-s3-bucket/)

**4. Add a Trigger to the Lambda function** 

Using EventBridge (CloudWatch Events) with the Schedule expression: cron(00 00 * * ? *) (Means it runs every day at midnight)

**5. Define following Environmental Variables in your Lambda function:**
* `CS_REGION` - Either NA (North America) or EU (Europe). Defaults to NA if nothing is defined
* `CS_STACKS` - One or more stacks to save the audit logs from. On the format: `<API_KEY1>,<MANAGEMENT_TOKEN1>;<API_KEY2>,<MANAGEMENT_TOKEN2>;etc..`.
* `S3_BUCKET` - Name of the bucket the logs will be uplodaded to. Make sure the Lambda function has access to write to the bucket via an IAM role (Step 3).

