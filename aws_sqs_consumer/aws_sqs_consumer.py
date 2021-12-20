from abc import ABC, abstractmethod
import boto3
import time

class Consumer(ABC):
    def __init__(self, queue_url, sqs_client=None, polling_wait_time_ms=0):
        self.queue_url = queue_url
        self.polling_wait_time_ms = polling_wait_time_ms
        self._sqs_cilent = sqs_client or boto3.client('sqs')

    @abstractmethod
    def handle_message(self, message):
        ...

    def handle_processing_exception(self, message, exception):
        pass

    def start(self):
        while True:
            response = self._sqs_cilent.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=0,
            )
            
            if not response.get('Messages', []):
                self._polling_wait()
                continue

            message = response['Messages'][0]
            try:
                self.handle_message(message)
                self._delete_message(message)
            except Exception as exception:
                self.handle_processing_exception(message, exception)
            finally:
                self._polling_wait()

    def _delete_message(self, message):
        response = self._sqs_cilent.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )

    def _polling_wait(self):
        time.sleep(self.polling_wait_time_ms / 1000)
