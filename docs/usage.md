# Usage

## Simple usage

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        # Write your logic to handle a single `message`.
        print("Received message: ", message.Body)

consumer = SimpleConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```

* `consumer.start()` will block the main thread.
* Consumer uses [SQS long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html#sqs-long-polling) by default with configurable wait time between polls (`polling_wait_time_ms`).
* By default, messages are processed one by one. The `handle_message` method must be finished for processing the next one. For receiving messages in batches, use the `batch_size` attribute. [See all attributes](#attributes).
* Messages are deleted from the queue after `handle_message` is successfully completed. 
* Raising an exception in the handler function will not delete the message from the queue. Define your behavior for handling exceptions by overriding `handle_processing_exception(message, exception)` method.  See [Handling exceptions](#handling-exceptions)

## Receiving messages in batches

SQS supports receiving messages in batches. Setting `batch_size > 1` will fetch multiple messages in a single call to SQS API. Override `handle_message_batch(messages)` method to process the message batch.

Note that only after `handle_message_batch` is finished, the next batch of messages is fetched. Maximum supported `batch_size` is `10`.

```python
from typing import List
from aws_sqs_consumer import Consumer, Message

class BatchConsumer(Consumer):
    def handle_message_batch(self, messages: List[Message]):
        print(f"Received {len(messages)} Messages")
        for message in messages:
            print(f"\t{message.Body}")

consumer = BatchConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    batch_size=5,
    polling_wait_time_ms=5,
)
consumer.start()
```

## Handling exceptions

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Processing message: {message.Body}")
        raise Exception("Something went wrong!")

    def handle_processing_exception(self, message: Message, exception):
        # Define your logic to handle exception
        print(f"Exception occured while processing: {exception}")

consumer = SimpleConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```

* Override `handle_batch_processing_exception(messages: List[Message], exception)` in case of `batch_size` > 1.

## Long and short polling

* **Short polling** - If you set `wait_time_seconds=0`, it is short polling. If you also set `polling_wait_time_ms=0` (which is default), you will be making a lot of (unregulated) HTTP calls to AWS.
* **Long polling** - With `wait_time_seconds > 0`, it is long polling.

For a detailed explanation, refer [Amazon SQS short and long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html).

## Running as a daemon

Currently, there is no built-in support for running as a daemon. But, you can use `nohup`.

```sh
nohup python my_sqs_consumer.py > sqs_consumer.log 2>&1 </dev/null &
```

## AWS Credentials

Consumer uses [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for interacting with SQS. Simplest option is to set the following environment variables:

```bash
export AWS_SECRET_ACCESS_KEY=...
export AWS_ACCESS_KEY_ID=...
```

If you want to manually configure the credentials, pass custom `boto3.Client` object to `Consumer`:

```python
import boto3
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Received message: {message.Body}")

sqs_client = boto3.client(
    'sqs',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    aws_session_token=SESSION_TOKEN
)

consumer = SimpleConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5,
    sqs_client=sqs_client
)
consumer.start()
```

See [`boto3` latest credentials guideline](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).