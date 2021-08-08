import os
import csv
import json
import boto3
import logging

from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()


def get_file(file):
    """
        Get file from S3

        :param file: S3 object key
        :type file: str

        :return contents: CSV data
        :rtype contents: list
    """

    s3 = session.client('s3')

    try:
        obj = s3.get_object(Bucket=os.environ['DATA_BUCKET'], Key=file)
        contents = obj['Body'].read().decode('utf-8').splitlines(True)
        return contents

    except Exception as e:
        logger.error(f"Error getting file {file}. Exception: {e}.")
        return None


def move_file(file):
    """
        Mark file as 'processed'

        :param file: S3 object key
        :type file: str

        :return: True if file was marked correctly, False o/w
        :rtype: bool
    """

    s3 = session.resource('s3')

    try:
        s3.Object(os.environ['DATA_BUCKET'], f"{file}.PROCESSED")\
            .copy_from(CopySource=f"{os.environ['DATA_BUCKET']}/{file}")
        s3.Object(os.environ['DATA_BUCKET'], file).delete()
        return True
    except Exception as e:
        logger.error(f"Error moving file {file}. Exception: {e}.")
        return False


def process_file(file):
    """
        Process CSV file

        :param file: S3 object key
        :type file: str

        :return: True if file processed correctly, False o/w
        :rtype: bool
    """

    try:
        file_contents = get_file(file)

        if file_contents:

            contents_reader = csv.reader(file_contents, delimiter=';', quotechar='"')

            header = next(contents_reader)
            header[0] = "ID"
            header[3] = "TIMESTAMP"

            dynamodb = session.resource('dynamodb')
            table = dynamodb.Table(os.environ['DATA_TABLE'])

            with table.batch_writer() as batch:
                for row in contents_reader:
                    row[0] = int(row[0])
                    row[3] = int(datetime.strptime(row[3], "%d/%m/%Y").timestamp())
                    item = dict(zip(header, row))
                    batch.put_item(Item=item)

            return move_file(file)

        else:
            return False

    except Exception as e:
        logger.error(f"Error processing file {file}. Exception: {e}")
        return False


def lambda_handler(event, context):
    """
        Lambda function handler

        :param event: Lambda event data
        :type event: dict

        :param context: Lambda runtime data
        :type context: dict
    """

    try:
        for record in event["Records"]:

            key = record["s3"]["object"]["key"]

            if process_file(key):
                logger.info(f"Processed file {key}.")

    except Exception as e:
        logger.error(f"Error processing event {json.dumps(event)}. Exception: {e}.")
