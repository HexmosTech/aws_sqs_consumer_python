# Python AWS SQS Consumer

![PyPI](https://img.shields.io/pypi/v/aws-sqs-consumer?color=blue)

Write Amazon Simple Queue Service (SQS) consumers in Python with simplified interface. Define your logic to process an SQS message. After you're done processing, messages are deleted from the queue.

Heavily inspired from [https://github.com/bbc/sqs-consumer](https://github.com/bbc/sqs-consumer), a similar JavaScript interface.

## Installation

```
pip install aws-sqs-consumer
```

## Usage

### Simple usage

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

### Receiving messages in batches

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

### Handling exceptions

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

### Long and short polling

* **Short polling** - If you set `wait_time_seconds=0`, it is short polling. If you also set `polling_wait_time_ms=0` (which is default), you will be making a lot of (unregulated) HTTP calls to AWS.
* **Long polling** - With `wait_time_seconds > 0`, it is long polling.

For a detailed explanation, refer [Amazon SQS short and long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html).

### AWS Credentials

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

## API

### `Consumer(...)`

Creates a new SQS consumer. Default parameters:

```python
consumer = Consumer(
    queue_url, # REQUIRED
    region="eu-west-1",
    sqs_client=None,
    attribute_names=[],
    message_attribute_names=[],
    batch_size=1,
    wait_time_seconds=1,
    visibility_timeout_seconds=None,
    polling_wait_time_ms=0
)
```

#### Attributes

| Attribute                                                                                                                     | Description                                                                                                                                                                                                                                                                                                                         | Default       | Example(s)                                                                                                                            |
|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `queue_url` (`str`)                                                                                                           | SQS Queue URL                                                                                                                                                                                                                                                                                                                       | **REQUIRED**  | `"https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue"`                                                                        |
| `region` (`str`)                                                                                                              | AWS region for internally creating an SQS client using `boto3`                                                                                                                                                                                                                                                                      | `"eu-west-1"` | `"us-east-1"`, `"ap-south-1"`                                                                                                         |
| `sqs_client` ([`boto3.SQS.Client`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#id57)) | Override this to pass your own SQS client. This takes precedence over `region`                                                                                                                                                                                                                                                      | `None`        | `sqs_client = boto3.client("sqs", region_name="ap-south-1")`                                                                          |
| `attribute_names` (`list`)                                                                                                    | List of attributes that need to be returned along with each message.                                                                                                                                                                                                                                                                | `[]`          | - `["All"]` - Returns all values.<br>- `["ApproximateFirstReceiveTimestamp", "ApproximateReceiveCount", "SenderId", "SentTimestamp"]` |
| `message_attribute_names` (`list`)                                                                                            | List of names of message attributes, i.e. metadata you have passed to each message while sending to the queue.                                                                                                                                                                                                                      | `[]`          | `["CustomAttr1", "CustomAttr2"]`                                                                                                      |
| `batch_size` (`int`)                                                                                                          | Number of messages to return at once. (Maximum `10`)<br><br>- If `batch_size = 1`, override `handle_message(message)` and `handle_processing_exception(message, exception)` methods.<br>- If `batch_size > 1`, override `handle_message_batch(messages)` and `handle_batch_processing_exception(messages, exception)` methods.<br>  | `1`           |                                                                                                                                       |
| `wait_time_seconds` (`int`)                                                                                                   | The duration (in seconds) for which the call waits for a message to arrive in the queue before returning. If a message is available, the call returns sooner than `wait_time_seconds`.                                                                                                                                              | `1`           |                                                                                                                                       |
| `visibility_timeout_seconds` (`int`)                                                                                          | The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved. <br><br>If this is `None`, visibility timeout of the queue is used.                                                                                                                                        | `None`        | `30`                                                                                                                                  |
| `polling_wait_time_ms` (`int`)                                                                                                | The duration (in ms) between two subsequent polls.                                                                                                                                                                                                                                                                                  | `0`           | `2000` (2 seconds)                                                                                                                    |

#### `consumer.start()`

Starts polling the queue. This blocks the main thread.

#### `consumer.stop()`

Stops polling the queue. You can use this method only if you run the `consumer` in a separate thread.

#### `handle_message(message)`

Override this method to define logic for handling a single message. By default, this does nothing (i.e. `pass`). This is called only if `batch_size=1`.

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Processing message: {message.Body}")
```

#### `handle_processing_exception(message, exception)`

Override this method to handle any exception processing the message, including message deletion. By default, stack trace is printed to the console. This is called only if `batch_size=1`.

See [Handling exceptions](#handling-exceptions).

#### `handle_message_batch(messages)`

Override this method to define logic for handling a message batch. By default, this does nothing (i.e. `pass`). This is called only if `batch_size > 1`.

See [Receiving messages in batches](#receiving-messages-in-batches).

#### `handle_batch_processing_exception(messages, exception)`

Override this method to handle any exception processing a message batch, including message batch deletion. By default, stack trace is printed to the console. This is called only if `batch_size > 1`.

```python
from typing import List
from aws_sqs_consumer import Consumer, Message

class BatchConsumer(Consumer):
    def handle_message_batch(self, messages: List[Message]):
        print(f"Received {len(messages)} Messages")
        raise Exception("Failed to process message batch")

    def handle_batch_processing_exception(messages: List[Message], exception):
        print(f"Exception occurred while processing message batch: {exception}")
```

### `Message`

`Message` represents a single SQS message. It is defined as a Python `dataclass` with the following attributes:

* `MessageId` (`str`) - A unique identifier for the message.
* `ReceiptHandle` (`str`) - An identifier associated with the act of receiving the message.
* `MD5OfBody` (`str`) - An MD5 digest of the non-URL-encoded message body string.
* `Body` (`str`) - The message's contents.
* `Attributes` (`Dict[str, str]`) - A map of the attributes requested in `attribute_names` parameter in `Consumer`.
* `MD5OfMessageAttributes` (`str`) - An MD5 digest of the non-URL-encoded message attribute string.
* `MessageAttributes` (`Dict[str, MessageAttributeValue]`) - Dictionary of user defined message attributes.

**Example:**

```python
def handle_message(self, message: Message):
    print("MessageID: ", message.MessageId)
    print("ReceiptHandle: ", message.ReceiptHandle)
    print("MD5OfBody: ", message.MD5OfBody)
    print("Body: ", message.Body)
    print("Attributes: ", message.Attributes)
```

```
MessageID:  29bab209-989d-41f3-85b4-c0e9f8d8b7a9
ReceiptHandle:  AQEBU2VaFVLF6eXzFVLwPIFCqrZC0twP+qzfy2mi...==
MD5OfBody:  c72b9698fa1927e1dd12d3cf26ed84b3
Body:  test message
Attributes:  {'ApproximateFirstReceiveTimestamp': '1640985674001'}
```

### `MessageAttributeValue`

`MessageAttributeValue` represents a user-defined SQS message attribute value. It is defined as a Python `dataclass` with the following attributes:

* `StringValue` (`str`) - attribute value, if it is a `str`.
* `BinaryValue` (`bytes`) - Binary type attributes can store any binary data, such as compressed data, encrypted data, or images.
* `DataType` (`str`) - SQS supports `String`, `Number`, and `Binary`. For the Number data type, you must use `StringValue`.

**Example:**

```python
def handle_message(self, message: Message):
    msg_attributes = message.MessageAttributes
    host = msg_attributes["host"].StringValue
    age  = msg_attributes["age"].StringValue

    print("Message body=", message.Body)
    print("Message attribute host=", host)
    print("Message attribute age=", age)
```

```
Message body=test message
Message attribute host=host001.example.com
Message attribute age=20
```

## FAQ

### Does this support parallelization?

No. A message is fetched from the queue, processed, next message is fetched, and so on.

However, you can run multiple copies of your consumer script on different instances. Make sure you set a sufficient visibility timeout while creating the SQS queue: 
* For example, consider you have set `5m` of visibility timeout and run two instances of the script. 
* If `Consumer 1` receives message `m1` at `11:00 AM`, it has to be processed and deleted before `11:05 AM`. Otherwise, `Consumer 2` can receive `m1` after `11:05 AM` resulting in duplication.

### How do I configure AWS access to the queue?

The consumer needs permission to **receive** and **delete** messages from the queue. Here is a sample IAM Policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage"],
            "Resource": [
                "arn:aws:sqs:eu-west-1:12345678901:test_queue",
            ]
        }
    ]
}
```
