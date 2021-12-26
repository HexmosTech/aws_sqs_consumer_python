import unittest
import threading
import time
from moto import mock_sqs
import boto3

from aws_sqs_consumer import Consumer


class TestConsumeMessage(unittest.TestCase):
    @mock_sqs
    def test_consume_message(self):
        messages = []
        class TestConsumer(Consumer):
            def handle_message(self, message):
                messages.append(message.Body)

        sqs = boto3.resource('sqs', region_name='eu-west-1')
        queue = sqs.create_queue(QueueName="test_queue")
        test_consumer = TestConsumer(queue_url=queue.url, region="eu-west-1")
        t1 = threading.Thread(target=test_consumer.start)
        t1.start()
        sqs_client = boto3.client('sqs', region_name='eu-west-1')
        sqs_client.send_message(
            QueueUrl=queue.url,
            MessageBody="test_message"
        )
        time.sleep(1)
        test_consumer.stop()
        t1.join()

        assert messages[0] == "test_message"
