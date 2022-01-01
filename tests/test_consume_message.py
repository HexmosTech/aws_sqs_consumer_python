import unittest
from moto import mock_sqs

from aws_sqs_consumer import Consumer, Message, MessageAttributeValue
from .utils import async_sqs


class TestConsumeMessage(unittest.TestCase):
    @mock_sqs
    def test_message_consume_body(self):
        messages = []

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                messages.append(message.Body)

        with async_sqs(TestConsumer) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], "test_message")

    @mock_sqs
    def test_message_handle_exception(self):
        exceptions = []

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                raise Exception("Failed to handle message")

            def handle_processing_exception(self, message: Message, exception):
                exceptions.append(exception)

        with async_sqs(TestConsumer) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        self.assertEqual(len(exceptions), 1)
        self.assertEqual(type(exceptions[0]), Exception)
        self.assertEqual(str(exceptions[0]), "Failed to handle message")

    @mock_sqs
    def test_message_deafult_fields(self):
        messages = []

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                messages.append(message)

        with async_sqs(TestConsumer) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        message = messages[0]
        self.assertTrue(message.MessageId)
        self.assertTrue(message.ReceiptHandle)
        self.assertTrue(message.MD5OfBody)
        self.assertTrue(message.Body)
        self.assertDictEqual(message.MessageAttributes, {})
        self.assertDictEqual(message.Attributes, {})

    @mock_sqs
    def test_message_with_attributes(self):
        messages = []

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                messages.append(message)

        attribute_names = [
            "SenderId",
            "SentTimestamp",
            "ApproximateReceiveCount",
            "ApproximateFirstReceiveTimestamp"
        ]
        with async_sqs(
            TestConsumer, attribute_names=attribute_names
        ) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        message = messages[0]
        self.assertSetEqual(set(message.Attributes.keys()),
                            set(attribute_names))

    @mock_sqs
    def test_message_with_message_attributes(self):
        messages = []

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                messages.append(message)

        message_attributes = {
            "attr1": {
                "DataType": "String",
                "StringValue": "attr1_value"
            },
            "attr2": {
                "DataType": "Binary",
                "BinaryValue": b"attr2_value"
            },
            "attr3": {
                "DataType": "Number",
                "StringValue": "123"
            }
        }

        with async_sqs(
            TestConsumer,
            message_attribute_names=list(message_attributes.keys())
        ) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message",
                MessageAttributes=message_attributes
            )

        message = messages[0]
        received_attrs = message.MessageAttributes
        self.assertEqual(
            received_attrs["attr1"],
            MessageAttributeValue(**message_attributes["attr1"])
        )
        self.assertEqual(
            received_attrs["attr2"],
            MessageAttributeValue(**message_attributes["attr2"])
        )
        self.assertEqual(
            received_attrs["attr3"],
            MessageAttributeValue(**message_attributes["attr3"])
        )

    @mock_sqs
    def test_message_visibility_timeout(self):
        messages = []
        exceptions = []
        attempted = False

        class TestConsumer(Consumer):
            def handle_message(self, message: Message):
                nonlocal attempted
                if not attempted:
                    attempted = True
                    raise Exception("handle exception")
                else:
                    messages.append(message.Body)

            def handle_processing_exception(self, message: Message, exception):
                exceptions.append(exception)

        with async_sqs(
            TestConsumer,
            timeout_seconds=10,
            visibility_timeout_seconds=5
        ) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message",
            )

        self.assertTrue(len(messages) == 1)
        self.assertEqual(messages[0], "test_message")

        self.assertEqual(len(exceptions), 1)
        self.assertEqual(type(exceptions[0]), Exception)
        self.assertEqual(str(exceptions[0]), "handle exception")
