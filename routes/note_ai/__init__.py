# note_ai package
# WhatsApp Notification System untuk Note Management

__version__ = '1.0.0'
__author__ = 'Note AI System'
__description__ = 'WhatsApp notification system untuk note management dengan mention detection'

# Import main components
from .utils.core.note_notification_handler import NoteNotificationHandler, notification_handler
from .services.whatsapp_service import WhatsAppNotificationService
from .utils.mention_parser import MentionParser
from .utils.message_formatter import MessageFormatter
from .config.wa_config import WhatsAppConfig
from .config.ai_config import AIConfig

__all__ = [
    'NoteNotificationHandler',
    'notification_handler',
    'WhatsAppNotificationService',
    'MentionParser',
    'MessageFormatter',
    'WhatsAppConfig',
    'AIConfig'
]