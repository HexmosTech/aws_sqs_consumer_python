# AWS SQS Consumer

## Installation

Currently available via [https://test.pypi.org/project/aws-sqs-consumer/](https://test.pypi.org/project/aws-sqs-consumer/)

```
pip install -i https://test.pypi.org/simple/ aws-sqs-consumer==0.0.5
```

## Usage

```python
from aws_sqs_consumer import Consumer

class MyConsumer(Consumer):
    def handle_message(self, message):
        print("Received message ", message['Body'])

consumer = MyConsumer(
    queue_url="https://sqs.us-east-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```