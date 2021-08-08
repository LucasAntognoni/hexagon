# Hexagon

Processing pipeline using Brazil's Government spending data. This pipeline uses AWS _Lambda_, _S3_, _DynamoDB_ and _CloudWatch_ services.

## Prerequisites

* `Python 3.7`
* `AWS Account`
* `AWS Account Credentials`

## Configuring

### Environment variables

Set the following variables in your environment:

* `AWS_ACCOUNT`
* `AWS_REGION`
* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`

### Python libraries

Install with `pip` the following libraries:

* `boto3`

## Usage

### Create
To set up the AWS resources stack, run:

```
python deploy.py create
```

### Update Stack
To update the AWS resources stack, run:

```
python deploy.py update
```

### Update Lambda
To publish a new lambda version, run:

```
python deploy.py lambda
```

### Delete
To delete the AWS resources, run:

```
python deploy.py delete
```

## Upload file
The example files are located in the **data** folder. To upload and process a file, run:

```
python deploy.py upload <filename>
```

The processing result will be stored in a DynamoDB table.

## Data Fields

The fields `Id Empenho` and `Data Emissão` were translated to the DynamoDB table as `ID` and `Timestamp`,
respectively.

The latter is a `Unix Timestamp` derived from the date field with `%d/%m/%Y` format.

## Data Source

* http://www.portaldatransparencia.gov.br/
  * Documentos de empenho, liquidação e pagamento
