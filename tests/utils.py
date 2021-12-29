import boto3
import contextlib
import threading
import time


@contextlib.contextmanager
def async_sqs(consumer_class, region="eu-west-1", timeout_seconds=1, **kwargs):
    sqs_client = boto3.client("sqs", region_name=region)
    queue = sqs_client.create_queue(QueueName="test_queue")
    consumer = consumer_class(
        queue_url=queue["QueueUrl"], region=region, **kwargs
    )

    # Run consumer in background thread
    thread = threading.Thread(target=consumer.start)
    thread.start()

    yield sqs_client, queue

    # Post context, stop the consumer
    time.sleep(timeout_seconds)
    consumer.stop()
    thread.join()
