# core/note_notification_handler.py
# Handler utama untuk notifikasi note dengan mention

import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Add parent directories to path untuk import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import konfigurasi
from config.wa_config import WhatsAppConfig
from config.ai_config import AIConfig

# Import services dan utils
from services.whatsapp_service import WhatsAppNotificationService
from utils.mention_parser import MentionParser
from utils.message_formatter import MessageFormatter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoteNotificationHandler:
    """Handler utama untuk mengelola notifikasi note dengan mention"""
    
    def __init__(self):
        try:
            # Initialize components
            self.wa_config = WhatsAppConfig()
            self.ai_config = AIConfig()
            self.whatsapp_service = WhatsAppNotificationService()
            self.mention_parser = MentionParser()
            self.message_formatter = MessageFormatter()
            
            logger.info("NoteNotificationHandler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NoteNotificationHandler: {str(e)}")
            raise
    
    def process_note_creation(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process note creation dan kirim notifikasi jika ada mention
        
        Args:
            note_data (Dict): Data note yang baru dibuat
            
        Returns:
            Dict: Result dari proses notifikasi
        """
        try:
            logger.info(f"Processing note creation for ID: {note_data.get('id_input', 'N/A')}")
            
            # Extract mentions dari title dan content
            mentions = self._extract_mentions_from_note(note_data)
            
            if not mentions:
                logger.info("No mentions found in note")
                return {
                    'success': True,
                    'message': 'Note created successfully, no mentions found',
                    'mentions_processed': 0,
                    'notifications_sent': 0
                }
            
            # Process mentions dan kirim notifikasi
            notification_results = self._send_mention_notifications(note_data, mentions)
            
            # Compile results
            result = self._compile_notification_results(note_data, mentions, notification_results)
            
            logger.info(f"Note processing completed: {result['notifications_sent']} notifications sent")
            return result
            
        except Exception as e:
            logger.error(f"Error processing note creation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process note notifications',
                'mentions_processed': 0,
                'notifications_sent': 0
            }
    
    def _extract_mentions_from_note(self, note_data: Dict[str, Any]) -> List[str]:
        """
        Extract mentions dari title dan content note
        
        Args:
            note_data (Dict): Data note
            
        Returns:
            List[str]: List mentions yang ditemukan
        """
        try:
            title = note_data.get('note_title', '')
            content = note_data.get('note_content', '')
            
            # Parse mentions dari title
            title_mentions = self.mention_parser.extract_mentions(title)
            
            # Parse mentions dari content
            content_mentions = self.mention_parser.extract_mentions(content)
            
            # Gabungkan dan remove duplicates
            all_mentions = list(set(title_mentions + content_mentions))
            
            # Validate mentions
            valid_mentions = []
            for mention in all_mentions:
                if self.mention_parser.is_valid_mention(mention):
                    valid_mentions.append(mention)
                else:
                    logger.warning(f"Invalid mention found: {mention}")
            
            logger.info(f"Found {len(valid_mentions)} valid mentions: {valid_mentions}")
            return valid_mentions
            
        except Exception as e:
            logger.error(f"Error extracting mentions: {str(e)}")
            return []
    
    def _send_mention_notifications(self, note_data: Dict[str, Any], 
                                  mentions: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Kirim notifikasi untuk semua mentions
        
        Args:
            note_data (Dict): Data note
            mentions (List): List mentions
            
        Returns:
            Dict: Results dari setiap notifikasi
        """
        notification_results = {}
        
        try:
            # Format messages untuk semua mentions
            formatted_messages = self.message_formatter.format_multiple_mentions(note_data, mentions)
            
            # Kirim notifikasi untuk setiap mention
            for mention in mentions:
                try:
                    # Get message untuk mention ini
                    message = formatted_messages.get(mention, '')
                    
                    if not message:
                        logger.error(f"No formatted message for mention: {mention}")
                        notification_results[mention] = {
                            'success': False,
                            'error': 'No formatted message available'
                        }
                        continue
                    
                    # Kirim notifikasi
                    result = self.whatsapp_service.send_note_notification(
                        note_data=note_data,
                        mentioned_users=[mention]
                    )
                    
                    notification_results[mention] = result
                    
                    # Log result
                    if result.get('success'):
                        logger.info(f"Notification sent successfully to {mention}")
                    else:
                        logger.error(f"Failed to send notification to {mention}: {result.get('error')}")
                    
                except Exception as e:
                    logger.error(f"Error sending notification to {mention}: {str(e)}")
                    notification_results[mention] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return notification_results
            
        except Exception as e:
            logger.error(f"Error in send_mention_notifications: {str(e)}")
            return {mention: {'success': False, 'error': str(e)} for mention in mentions}
    
    def _compile_notification_results(self, note_data: Dict[str, Any], 
                                    mentions: List[str], 
                                    notification_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compile hasil notifikasi menjadi summary
        
        Args:
            note_data (Dict): Data note
            mentions (List): List mentions
            notification_results (Dict): Results dari notifikasi
            
        Returns:
            Dict: Summary hasil
        """
        try:
            successful_notifications = []
            failed_notifications = []
            
            # Analyze results
            for mention, result in notification_results.items():
                if result.get('success'):
                    successful_notifications.append(mention)
                else:
                    failed_notifications.append({
                        'mention': mention,
                        'error': result.get('error', 'Unknown error')
                    })
            
            # Create summary
            summary = {
                'success': len(failed_notifications) == 0,
                'note_id': note_data.get('id_input', 'N/A'),
                'note_title': note_data.get('note_title', 'N/A'),
                'created_by': note_data.get('created_by', 'N/A'),
                'mentions_processed': len(mentions),
                'notifications_sent': len(successful_notifications),
                'notifications_failed': len(failed_notifications),
                'successful_mentions': successful_notifications,
                'failed_mentions': failed_notifications,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add message
            if summary['success']:
                summary['message'] = f"All {len(mentions)} notifications sent successfully"
            else:
                summary['message'] = f"{len(successful_notifications)} of {len(mentions)} notifications sent successfully"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error compiling notification results: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to compile notification results',
                'mentions_processed': len(mentions),
                'notifications_sent': 0,
                'notifications_failed': len(mentions)
            }
    
    def test_notification_system(self, test_note_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Test sistem notifikasi dengan data dummy
        
        Args:
            test_note_data (Dict, optional): Data note untuk test
            
        Returns:
            Dict: Hasil test
        """
        try:
            logger.info("Starting notification system test")
            
            # Use provided test data atau buat dummy data
            if not test_note_data:
                test_note_data = {
                    'id_input': 'TEST-001',
                    'note_title': '@imam Test Notification System',
                    'note_content': 'Ini adalah test notifikasi sistem. Mohon konfirmasi jika pesan ini diterima.',
                    'created_by': 'System Test',
                    'table_source': 'table_design',
                    'created_at': datetime.now().isoformat()
                }
            
            # Process test note
            result = self.process_note_creation(test_note_data)
            
            # Add test info
            result['test_mode'] = True
            result['test_data'] = test_note_data
            
            logger.info(f"Notification system test completed: {result.get('message')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in notification system test: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Notification system test failed',
                'test_mode': True
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status sistem notifikasi
        
        Returns:
            Dict: Status sistem
        """
        try:
            status = {
                'system_status': 'operational',
                'components': {
                    'whatsapp_service': 'initialized',
                    'mention_parser': 'initialized',
                    'message_formatter': 'initialized',
                    'wa_config': 'loaded',
                    'ai_config': 'loaded'
                },
                'supported_mentions': list(self.wa_config.USER_PHONE_MAPPING.keys()),
                'total_users': len(self.wa_config.USER_PHONE_MAPPING),
                'timestamp': datetime.now().isoformat()
            }
            
            # Test basic functionality
            test_mentions = self.mention_parser.extract_mentions('@imam test')
            status['mention_parser_test'] = 'passed' if test_mentions else 'failed'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'system_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Instance global untuk digunakan di module lain
notification_handler = NoteNotificationHandler()