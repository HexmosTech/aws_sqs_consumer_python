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
