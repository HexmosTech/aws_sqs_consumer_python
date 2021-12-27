# AWS SQS Consumer

## Installation

Currently available via [https://test.pypi.org/project/aws-sqs-consumer/](https://test.pypi.org/project/aws-sqs-consumer/)

```
pip install -i https://test.pypi.org/simple/ aws-sqs-consumer
```

## Usage

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print("Received message: ", message.Body)

consumer = SimpleConsumer(
    queue_url="https://sqs.us-east-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```

**Batch processing**

```python
from typing import List
from aws_sqs_consumer import Consumer, Message

class BatchConsumer(Consumer):
    def handle_message_batch(self, messages: List[Message]):
        print(f"Received {len(messages)} Messages")
        for message in messages:
            print(f"\t{message.Body}")

consumer = BatchConsumer(
    queue_url="https://sqs.us-east-1.amazonaws.com/12345678901/test_queue",
    batch_size=5,
    polling_wait_time_ms=5,
)
consumer.start()
```