import unittest

from aws_sqs_consumer import Message, MessageAttributeValue


class TestMessageAttributeValueParse(unittest.TestCase):
    def test_default_values(self):
        attribute_value_dict = {}
        attribute_value = MessageAttributeValue.parse(attribute_value_dict)

        self.assertEqual(attribute_value.StringValue, "")
        self.assertEqual(attribute_value.BinaryValue, b"")
        self.assertEqual(attribute_value.StringListValues, [])
        self.assertEqual(attribute_value.BinaryListValues, [])
        self.assertEqual(attribute_value.DataType, "")

    def test_string_value(self):
        attribute_value_dict = {
            "StringValue": "lorem ipsum",
            "DataType": "String"
        }
        attribute_value = MessageAttributeValue.parse(attribute_value_dict)

        self.assertEqual(attribute_value.StringValue, "lorem ipsum")
        self.assertEqual(attribute_value.DataType, "String")

    def test_binary_value(self):
        attribute_value_dict = {
            "BinaryValue": b"lorem ipsum",
            "DataType": "Binary"
        }
        attribute_value = MessageAttributeValue.parse(attribute_value_dict)

        self.assertEqual(attribute_value.BinaryValue, b"lorem ipsum")
        self.assertEqual(attribute_value.DataType, "Binary")

    def test_number_type(self):
        attribute_value_dict = {
            "StringValue": "123",
            "DataType": "Number"
        }
        attribute_value = MessageAttributeValue.parse(attribute_value_dict)

        self.assertEqual(attribute_value.StringValue, "123")
        self.assertEqual(attribute_value.DataType, "Number")


class TestMessageParse(unittest.TestCase):
    def test_default_values(self):
        message_dict = {}
        message = Message.parse(message_dict)

        self.assertEqual(message.MessageId, "")
        self.assertEqual(message.ReceiptHandle, "")
        self.assertEqual(message.MD5OfBody, "")
        self.assertEqual(message.Body, "")
        self.assertEqual(message.Attributes, {})
        self.assertEqual(message.MD5OfMessageAttributes, "")
        self.assertEqual(message.MessageAttributes, {})

    def test_simple_message(self):
        message_dict = {
            "MessageId": "82726578-6b0g-4769-a48c-k4ce283f572d",
            "ReceiptHandle": "AQEB/GiDL/TO==",
            "MD5OfBody": "bbf9afe7431caf5f89a608bc31e8d822",
            "Body": "test body",
            "MD5OfMessageAttributes": "576131c4dd9dc86e105550adc3ff8ca4"
        }
        message = Message.parse(message_dict)

        self.assertEqual(message.MessageId,
                         "82726578-6b0g-4769-a48c-k4ce283f572d")
        self.assertEqual(message.ReceiptHandle, "AQEB/GiDL/TO==")
        self.assertEqual(message.MD5OfBody, "bbf9afe7431caf5f89a608bc31e8d822")
        self.assertEqual(message.Body, "test body")
        self.assertEqual(message.Attributes, {})
        self.assertEqual(message.MD5OfMessageAttributes,
                         "576131c4dd9dc86e105550adc3ff8ca4")
        self.assertEqual(message.MessageAttributes, {})

    def test_message_with_attributes(self):
        message_dict = {
            "MessageId": "82726578-6b0g-4769-a48c-k4ce283f572d",
            "ReceiptHandle": "AQEB/GiDL/TO==",
            "MD5OfBody": "bbf9afe7431caf5f89a608bc31e8d822",
            "Body": "test body",
            "Attributes": {
                "ApproximateFirstReceiveTimestamp": "1640500665000"
            },
            "MD5OfMessageAttributes": "576131c4dd9dc86e105550adc3ff8ca4"
        }
        message = Message.parse(message_dict)

        self.assertEqual(
            message.Attributes,
            {"ApproximateFirstReceiveTimestamp": "1640500665000"}
        )

    def test_message_with_message_attributes(self):
        message_dict = {
            "MessageId": "82726578-6b0g-4769-a48c-k4ce283f572d",
            "ReceiptHandle": "AQEB/GiDL/TO==",
            "MD5OfBody": "bbf9afe7431caf5f89a608bc31e8d822",
            "Body": "test body",
            "Attributes": {
                "ApproximateFirstReceiveTimestamp": "1640500665000"
            },
            "MD5OfMessageAttributes": "576131c4dd9dc86e105550adc3ff8ca4",
            "MessageAttributes": {
                "host": {
                    "StringValue": "host001.example.com",
                    "DataType": "String"
                },
                "port": {
                    "StringValue": "8000",
                    "DataType": "Number"
                }
            }
        }
        message = Message.parse(message_dict)
        message_attributes = message.MessageAttributes

        self.assertEqual(
            message_attributes["host"].StringValue, "host001.example.com")
        self.assertEqual(message_attributes["host"].DataType, "String")
        self.assertEqual(message_attributes["port"].StringValue, "8000")
        self.assertEqual(message_attributes["port"].DataType, "Number")
