from pathlib import Path
from single_source import get_version

from .consumer import Consumer
from .message import MessageAttributeValue, Message
from .error import SQSException

__version__ = get_version(__name__, Path(__file__).parent.parent)
__all__ = ["Consumer", "MessageAttributeValue", "Message", "SQSException"]
