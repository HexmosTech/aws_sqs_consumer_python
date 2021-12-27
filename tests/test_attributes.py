import unittest

from aws_sqs_consumer import Consumer, Message


class SimpleSQSConsumer(Consumer):
    def handle_message(self, message: Message):
        pass


class TestConsumerAttributes(unittest.TestCase):
    def setUp(self) -> None:
        self.queue_url = "https://eu-west-1.queue.amazonaws.com/123456789012/test_queue"

    def test_no_abstract_initialization(self):
        with self.assertRaisesRegex(TypeError, "abstract methods handle_message"):
            Consumer(queue_url=self.queue_url)

    def test_mandatory_queue_url(self):
        with self.assertRaisesRegex(TypeError, 'queue_url'):
            SimpleSQSConsumer()

    def test_default_attributes(self):
        consumer = SimpleSQSConsumer(queue_url=self.queue_url)
        self.assertEqual(consumer.queue_url, self.queue_url)
        self.assertEqual(consumer.attribute_names, [])
        self.assertEqual(consumer.message_attribute_names, [])
        self.assertEqual(consumer.wait_time_seconds, 1)
        self.assertEqual(consumer.visibility_timeout_seconds, None)
        self.assertEqual(consumer.polling_wait_time_ms, 0)
        self.assertEqual(consumer.receive_request_attempt_id, None)

    def test_all_attributes(self):
        consumer = SimpleSQSConsumer(
            queue_url=self.queue_url,
            attribute_names=[
                'ApproximateFirstReceiveTimestamp', 'MaximumMessageSize'
            ],
            message_attribute_names=['attr1', 'attr2'],
            wait_time_seconds=10,
            visibility_timeout_seconds=30,
            polling_wait_time_ms=1000
        )
        self.assertEqual(consumer.queue_url, self.queue_url)
        self.assertEqual(
            consumer.attribute_names,
            ['ApproximateFirstReceiveTimestamp', 'MaximumMessageSize']
        )
        self.assertEqual(consumer.message_attribute_names, ['attr1', 'attr2'])
        self.assertEqual(consumer.wait_time_seconds, 10)
        self.assertEqual(consumer.visibility_timeout_seconds, 30)
        self.assertEqual(consumer.polling_wait_time_ms, 1000)

    def test_attr_fifo_request_attempt_id(self):
        consumer = SimpleSQSConsumer(
            queue_url=self.queue_url,
            receive_request_attempt_id='test_id'
        )
        self.assertEqual(consumer.receive_request_attempt_id, 'test_id')
