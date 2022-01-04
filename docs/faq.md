# FAQ

## Does this support parallelization?

No. A message is fetched from the queue, processed, next message is fetched, and so on.

However, you can run multiple copies of your consumer script on different instances. Make sure you set a sufficient visibility timeout while creating the SQS queue: 
* For example, consider you have set `5m` of visibility timeout and run two instances of the script. 
* If `Consumer 1` receives message `m1` at `11:00 AM`, it has to be processed and deleted before `11:05 AM`. Otherwise, `Consumer 2` can receive `m1` after `11:05 AM` resulting in duplication.

## How do I configure AWS access to the queue?

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
