import os
import sys
import shutil

import boto3

session = boto3.session.Session(
    region_name=os.environ['AWS_REGION'],
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)


def build_lambda():
    """
        Creates Lambda deployment package
    """

    try:
        os.system("mkdir -p ./build")
        os.system("cp -r ./lambda ./build")
        os.system("pip3 install -r ./build/lambda/requirements.txt -t ./build/lambda")
        shutil.make_archive("./build/lambda", 'zip', "./build/lambda")
        os.system("rm -rf ./build/lambda")

        print("Lambda deployment package built!")

    except Exception as e:
        print(f"Error building deployment package. Exception: {e}.")


def upload_lambda():
    """
        Uploads Lambda deployment package to S3
    """

    s3 = session.resource('s3')

    try:
        s3.Bucket(f"lambda-source-{os.environ['AWS_ACCOUNT']}").upload_file('./build/lambda.zip', 'lambda.zip')
        print("Lambda deployment package uploaded to S3!")

    except Exception as e:
        print(f"Error uploading deployment package. Exception: {e}.")


def update_lambda():
    """
        Publishes a new Lambda version
    """

    client = session.client('lambda')

    try:
        client.update_function_code(
            FunctionName='process_csv',
            S3Key='lambda.csv',
            S3Bucket=f"lambda-source-{os.environ['AWS_ACCOUNT']}",
            Publish=True
        )
        print("Lambda function published!")

    except Exception as e:
        print(f"Error publishing lambda. Exception: {e}.")


def create_bucket():
    """
        Creates S3 Bucket for Lambda source code
    """

    s3 = session.resource('s3')

    try:
        s3.create_bucket(Bucket=f"lambda-source-{os.environ['AWS_ACCOUNT']}", ACL='private')
        print('Created S3 bucket!')

    except Exception as e:
        print(f"Error creating S3 bucket. Exception: {e}.")


def delete_bucket():
    """
        Deletes S3 Bucket for Lambda source code
    """

    s3 = session.resource('s3')

    try:
        bucket = s3.Bucket(f"lambda-source-{os.environ['AWS_ACCOUNT']}")
        bucket.objects.all().delete()
        bucket.delete()
        print('Deleted S3 bucket!')

    except Exception as e:
        print(f"Error deleting S3 bucket. Exception: {e}.")


def empty_bucket():
    """
        Deletes S3 Bucket objects
    """

    s3 = session.resource('s3')

    try:
        bucket = s3.Bucket(f"data-storage-{os.environ['AWS_ACCOUNT']}")
        bucket.objects.all().delete()
        print('Deleted S3 objects!')

    except Exception as e:
        print(f"Error deleting S3 objects. Exception: {e}.")


def create_stack():
    """
        Creates CloudFormation Stack
    """

    try:
        cf = session.client("cloudformation")

        with open("stack.yml") as file:
            template = file.read()

        cf.validate_template(TemplateBody=template)

        cf.create_stack(
            StackName='data-processing',
            TemplateBody=template,
            TimeoutInMinutes=10,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure='DO_NOTHING',
            Parameters=[
                {'ParameterKey': 'BucketName', 'ParameterValue': f"data-storage-{os.environ['AWS_ACCOUNT']}"}
            ]
        )

        print("Creating CloudFormation stack. Check the service console for more information.")

    except Exception as e:
        print(f"Error creating stack. Exception: {e}.")


def update_stack():
    """
        Updates CloudFormation Stack
    """

    try:
        cf = session.client("cloudformation")

        with open("stack.yml") as file:
            template = file.read()

        cf.validate_template(TemplateBody=template)

        cf.update_stack(
            StackName='data-processing',
            TemplateBody=template,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=[
                {'ParameterKey': 'BucketName', 'ParameterValue': f"data-storage-{os.environ['AWS_ACCOUNT']}"}
            ]
        )

        print("Updating CloudFormation stack. Check the service console for more information.")

    except Exception as e:
        print(f"Error updating stack. Exception: {e}.")


def delete_stack():
    """
        Deletes CloudFormation Stack
    """

    try:
        cf = session.client("cloudformation")
        cf.delete_stack(StackName='data-processing')

        print("Deleting CloudFormation stack. Check the service console for more information.")

    except Exception as e:
        print(f"Error deleting stack. Exception: {e}.")


def upload_file(file):
    """
        Upload file to S3 for processing
    """

    try:
        if file in os.listdir('./data'):
            s3 = session.resource('s3')
            s3.Bucket(f"data-storage-{os.environ['AWS_ACCOUNT']}").upload_file(f"./data/{file}", file)
            print(f"Uploaded {file} with success!")
        else:
            print(f"File does not exist!")

    except Exception as e:
        print(f"Error uploading stack. Exception: {e}.")


if __name__ == '__main__':

    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print("Available commands:\n\n\t>create: Deploy stack"
              "\n\n\t>update: Update stack and lambda"
              "\n\n\t>delete: Delete stack, lambda and S3 bucket"
              "\n\n\t>lambda: Update lambda")
    elif sys.argv[1] == 'create':
        create_bucket()
        build_lambda()
        upload_lambda()
        create_stack()
    elif sys.argv[1] == 'update':
        build_lambda()
        upload_lambda()
        update_lambda()
        update_stack()
    elif sys.argv[1] == 'delete':
        delete_bucket()
        empty_bucket()
        delete_stack()
    elif sys.argv[1] == 'lambda':
        build_lambda()
        upload_lambda()
        update_lambda()
    elif sys.argv[1] == 'upload':
        if len(sys.argv) < 3:
            print("Missing parameter: file!")
        else:
            upload_file(sys.argv[2])
    else:
        print("Wrong command! Type 'help' to see available options.")
