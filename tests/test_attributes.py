import unittest

from aws_sqs_consumer import Consumer

class SimpleSQSConsumer(Consumer):
    def handle_message(self, message):
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
        sqs_consumer = SimpleSQSConsumer(queue_url=self.queue_url)
        self.assertEqual(sqs_consumer.queue_url, self.queue_url)
        self.assertEqual(sqs_consumer.attribute_names, [])
        self.assertEqual(sqs_consumer.polling_wait_time_ms, 0)
    