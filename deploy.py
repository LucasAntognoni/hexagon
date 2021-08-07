import os
import sys
import shutil

import boto3

session = boto3.session.Session(profile_name=os.environ['AWS_PROFILE'])


def build_lambda():
    try:
        os.system("mkdir -p build")
        os.system("cp -r /build/lambda build")
        os.system("pip3 install -r ./build/lambda/requirements.txt -t ./build/lambda")
        shutil.make_archive("./build/lambda", 'zip', "./build/lambda")
        os.system("rm -rf ./build/lambda")

    except Exception as e:
        print(f"Error building lambda. Exception: {e}.")


def upload_lambada():
    try:
        s3 = session.resource('s3')
        s3.Bucket('lambda-source').upload_file('./build/lambda.zip', 'lambda.zip')
    except Exception as e:
        print(f"Error uploading lambda. Exception: {e}.")


def create_stack():
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
        )

    except Exception as e:
        print(f"Error creating stack. Exception: {e}.")


def update_stack():
    try:
        cf = session.client("cloudformation")

        with open("stack.yml") as file:
            template = file.read()

        cf.validate_template(TemplateBody=template)

        cf.update_stack(
            StackName='data-processing',
            TemplateBody=template,
            TimeoutInMinutes=10,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure='DO_NOTHING',
        )

    except Exception as e:
        print(f"Error updating stack. Exception: {e}.")


def delete_stack():
    try:
        cf = session.client("cloudformation")
        cf.delete_stack(StackName='data-processing')

    except Exception as e:
        print(f"Error deleting stack. Exception: {e}.")


if __name__ == '__main__':

    if sys.argv[2] == 'create':
        create_stack()
    elif sys.argv[2] == 'update':
        update_stack()
    elif sys.argv[2] == 'delete':
        delete_stack()
    else:
        print("Wrong command!")
