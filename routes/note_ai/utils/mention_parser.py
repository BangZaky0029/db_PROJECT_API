# utils/mention_parser.py
# Parser untuk mendeteksi @mentions dalam note title

import re
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentionParser:
    """Parser untuk mendeteksi dan memproses @mentions dalam note"""
    
    def __init__(self):
        # Pattern untuk mendeteksi @mentions
        self.mention_pattern = r'@([a-zA-Z0-9_]+)'
        
        # Daftar user yang valid untuk di-mention
        self.valid_users = [
            'vinka', 'desi', 'david', 'ikbal', 'untung', 'imam'
        ]
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Ekstrak semua @mentions dari text
        
        Args:
            text (str): Text yang akan dianalisis
            
        Returns:
            List[str]: List mentions yang ditemukan (contoh: ['@imam', '@lilis'])
        """
        try:
            if not text:
                return []
            
            # Cari semua pattern @username
            matches = re.findall(self.mention_pattern, text.lower())
            
            # Format dengan @ dan filter yang valid
            mentions = []
            for match in matches:
                mention = f"@{match}"
                if match in self.valid_users:
                    mentions.append(mention)
                    logger.info(f"Valid mention found: {mention}")
                else:
                    logger.warning(f"Invalid mention found: {mention}")
            
            # Remove duplicates while preserving order
            unique_mentions = list(dict.fromkeys(mentions))
            
            return unique_mentions
            
        except Exception as e:
            logger.error(f"Error extracting mentions: {str(e)}")
            return []
    
    def has_mentions(self, text: str) -> bool:
        """
        Cek apakah text mengandung @mentions
        
        Args:
            text (str): Text yang akan dicek
            
        Returns:
            bool: True jika ada mentions, False jika tidak
        """
        mentions = self.extract_mentions(text)
        return len(mentions) > 0
    
    def get_mention_count(self, text: str) -> int:
        """
        Hitung jumlah @mentions dalam text
        
        Args:
            text (str): Text yang akan dihitung
            
        Returns:
            int: Jumlah mentions
        """
        mentions = self.extract_mentions(text)
        return len(mentions)
    
    def is_valid_mention(self, mention: str) -> bool:
        """
        Cek apakah mention adalah user yang valid
        
        Args:
            mention (str): Mention yang akan dicek (dengan atau tanpa @)
            
        Returns:
            bool: True jika valid, False jika tidak
        """
        try:
            # Normalize mention
            if mention.startswith('@'):
                username = mention[1:].lower()
            else:
                username = mention.lower()
            
            return username in self.valid_users
            
        except Exception as e:
            logger.error(f"Error validating mention {mention}: {str(e)}")
            return False
    
    def validate_mentions(self, mentions: List[str]) -> Dict[str, Any]:
        """
        Validasi list mentions
        
        Args:
            mentions (List[str]): List mentions yang akan divalidasi
            
        Returns:
            Dict: Status validasi dengan detail
        """
        try:
            valid_mentions = []
            invalid_mentions = []
            
            for mention in mentions:
                # Normalize mention
                if not mention.startswith('@'):
                    mention = f"@{mention}"
                
                username = mention[1:].lower()  # Remove @ and lowercase
                
                if username in self.valid_users:
                    valid_mentions.append(mention.lower())
                else:
                    invalid_mentions.append(mention)
            
            return {
                "valid_mentions": valid_mentions,
                "invalid_mentions": invalid_mentions,
                "total_valid": len(valid_mentions),
                "total_invalid": len(invalid_mentions),
                "is_all_valid": len(invalid_mentions) == 0
            }
            
        except Exception as e:
            logger.error(f"Error validating mentions: {str(e)}")
            return {
                "valid_mentions": [],
                "invalid_mentions": mentions,
                "total_valid": 0,
                "total_invalid": len(mentions),
                "is_all_valid": False
            }
    
    def parse_note_for_mentions(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse note data untuk mencari mentions
        
        Args:
            note_data (Dict): Data note yang berisi title, content, dll
            
        Returns:
            Dict: Hasil parsing dengan detail mentions
        """
        try:
            title = note_data.get('note_title', '')
            content = note_data.get('note_content', '')
            
            # Extract mentions dari title dan content
            title_mentions = self.extract_mentions(title)
            content_mentions = self.extract_mentions(content)
            
            # Gabungkan dan remove duplicates
            all_mentions = list(dict.fromkeys(title_mentions + content_mentions))
            
            # Validasi mentions
            validation = self.validate_mentions(all_mentions)
            
            result = {
                "note_id": note_data.get('id_note'),
                "id_input": note_data.get('id_input'),
                "table_source": note_data.get('table_source'),
                "title_mentions": title_mentions,
                "content_mentions": content_mentions,
                "all_mentions": all_mentions,
                "validation": validation,
                "has_mentions": len(all_mentions) > 0,
                "should_notify": validation['total_valid'] > 0
            }
            
            if result['should_notify']:
                logger.info(f"Note {note_data.get('id_note')} has valid mentions: {validation['valid_mentions']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing note for mentions: {str(e)}")
            return {
                "note_id": note_data.get('id_note'),
                "id_input": note_data.get('id_input'),
                "table_source": note_data.get('table_source'),
                "title_mentions": [],
                "content_mentions": [],
                "all_mentions": [],
                "validation": {
                    "valid_mentions": [],
                    "invalid_mentions": [],
                    "total_valid": 0,
                    "total_invalid": 0,
                    "is_all_valid": False
                },
                "has_mentions": False,
                "should_notify": False
            }
    
    def get_notification_summary(self, parse_result: Dict[str, Any]) -> str:
        """
        Generate summary untuk logging/debugging
        
        Args:
            parse_result (Dict): Hasil dari parse_note_for_mentions
            
        Returns:
            str: Summary text
        """
        try:
            if not parse_result['should_notify']:
                return "No valid mentions found, no notifications will be sent."
            
            valid_mentions = parse_result['validation']['valid_mentions']
            summary = f"Found {len(valid_mentions)} valid mention(s): {', '.join(valid_mentions)}. "
            summary += f"Notifications will be sent to these users."
            
            if parse_result['validation']['total_invalid'] > 0:
                invalid_mentions = parse_result['validation']['invalid_mentions']
                summary += f" Invalid mentions ignored: {', '.join(invalid_mentions)}."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error generating notification summary."

# Instance global untuk digunakan di module lain
mention_parser = MentionParser()