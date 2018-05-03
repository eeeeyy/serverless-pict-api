import json
import unittest
from unittest import mock

from src import get_image
from tests.testing.dynamodb_testing_util import DynamoDbTestingUtil

dynamodb_local = DynamoDbTestingUtil.create_dynamodb_local_resource()


class TestGetImage(unittest.TestCase):

    def setUp(self):
        dynamodb_local.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'photo_id',
                    'AttributeType': 'S'
                }
            ],
            TableName='photos',
            KeySchema=[
                {
                    'AttributeName': 'photo_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
        )

    def tearDown(self):
        DynamoDbTestingUtil.delete_table('photos')

    @mock.patch('boto3.resource')
    def test_handler_ok(self, mock_resource):
        table = dynamodb_local.Table('photos')
        table.put_item(Item={
            'photo_id': 'photo_id'
        })

        mock_resource.return_value = dynamodb_local

        event = {
            'pathParameters': {
                'image_id': 'photo_id'
            }
        }
        actual = get_image.handler(event, None)
        self.assertEqual(actual['statusCode'], 200)
        self.assertEqual(actual['body'], json.dumps({'photo_id': 'photo_id'}))

    @mock.patch('boto3.resource')
    def test_handler_fail_ifRequiredParamsIsInvalid(self, mock_resource):
        mock_resource.return_value = dynamodb_local
        event = {
            'pathParameters': {}
        }

        actual = get_image.handler(event, None)
        self.assertEqual(actual['statusCode'], 400)

    @mock.patch('boto3.resource')
    def test_handler_fail_ifPhotoResourceNotFound(self, mock_resource):
        table = dynamodb_local.Table('photos')
        table.put_item(Item={
            'photo_id': 'photo_id'
        })

        mock_resource.return_value = dynamodb_local

        event = {
            'pathParameters': {
                'image_id': 'not_found'
            }
        }
        actual = get_image.handler(event, None)
        self.assertEqual(actual['statusCode'], 404)
