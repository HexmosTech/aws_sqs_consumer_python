from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MessageAttributeValue:
    """Class representing SQS message attribute value"""
    StringValue: str = ""
    BinaryValue: bytes = b""
    StringListValues: List[str] = field(default_factory=list)
    BinaryListValues: List[bytes] = field(default_factory=list)
    DataType: str = ""

    @staticmethod
    def parse(attribute_value_dict):
        return MessageAttributeValue(**attribute_value_dict)


@dataclass
class Message:
    """Class representing a single SQS message"""
    MessageId: str = ""
    ReceiptHandle: str = ""
    MD5OfBody: str = ""
    Body: str = ""
    Attributes: Dict[str, str] = field(default_factory=dict)
    MD5OfMessageAttributes: str = ""
    MessageAttributes: Dict[str, MessageAttributeValue] = field(
        default_factory=dict
    )

    @staticmethod
    def parse(message_dict):
        message_attributes_dict = message_dict.get("MessageAttributes", {})
        message_attributes = {
            attribute: MessageAttributeValue.parse(attribute_value)
            for attribute, attribute_value in message_attributes_dict.items()
        }
        message = Message(**message_dict)
        message.MessageAttributes = message_attributes
        return message
