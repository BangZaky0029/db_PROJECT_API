# utils/message_formatter.py
# Message formatter untuk WhatsApp notifications

import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageFormatter:
    """Formatter untuk pesan WhatsApp notifications"""
    
    def __init__(self):
        # Emoji dan formatting constants
        self.emojis = {
            'notification': '🔔',
            'note': '📝',
            'content': '📄',
            'user': '👤',
            'date': '📅',
            'id': '🆔',
            'source': '📊',
            'urgent': '🚨',
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️'
        }
        
        # Template pesan
        self.templates = {
            'note_mention': self._get_note_mention_template(),
            'urgent_note': self._get_urgent_note_template(),
            'simple_note': self._get_simple_note_template()
        }
    
    def _get_note_mention_template(self) -> str:
        """Template untuk notifikasi mention biasa"""
        return (
            "{notification} *NOTIFIKASI NOTE*\n\n"
            "From : {created_by}\n"
            "Halo {mentioned_user},\n"
            "Anda di-mention dalam note baru:\n\n"
            "{note} *Judul:* {title}\n"
            "id_input : {id_input}\n"
            "Sumber : {table_source}\n\n"
            "{content} {content_text}\n"
        )
    
    def _get_urgent_note_template(self) -> str:
        """Template untuk notifikasi urgent"""
        return (
            "{urgent} *NOTIFIKASI URGENT* {urgent}\n\n"
            "Halo {mentioned_user},\n\n"
            "Anda di-mention dalam note URGENT:\n\n"
            "{note} *Judul:* {title}\n\n"
            "id_input : {id_input}\n\n"
            "Sumber : {table_source}\n\n"
            "{content} {content_text}\n\n"
            "⚡ *MOHON SEGERA DITINDAKLANJUTI* ⚡\n\n"
            "From : {created_by}"
        )
    
    def _get_simple_note_template(self) -> str:
        """Template untuk notifikasi sederhana"""
        return (
            "{notification} *NOTE BARU*\n\n"
            "Halo {mentioned_user},\n\n"
            "{note} {title}\n\n"
            "id_input : {id_input}\n\n"
            "Sumber : {table_source}\n\n"
            "{content} {content_text}\n\n"
            "From : {created_by}"
        )
    
    def format_note_notification(self, note_data: Dict[str, Any], mentioned_user: str, 
                               template_type: str = 'note_mention') -> str:
        """
        Format pesan notifikasi note
        
        Args:
            note_data (Dict): Data note
            mentioned_user (str): User yang di-mention
            template_type (str): Jenis template ('note_mention', 'urgent_note', 'simple_note')
            
        Returns:
            str: Pesan yang sudah diformat
        """
        try:
            # Ambil template
            template = self.templates.get(template_type, self.templates['note_mention'])
            
            # Format data
            formatted_data = self._prepare_note_data(note_data, mentioned_user)
            
            # Format pesan
            message = template.format(**formatted_data)
            
            # Bersihkan pesan dari karakter yang tidak diinginkan
            message = self._clean_message(message)
            
            logger.info(f"Message formatted for {mentioned_user} using template {template_type}")
            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return self._get_fallback_message(note_data, mentioned_user)
    
    def _prepare_note_data(self, note_data: Dict[str, Any], mentioned_user: str) -> Dict[str, str]:
        """Prepare dan format data note untuk template"""
        try:
            # Format tanggal
            created_at = note_data.get('created_at', datetime.now())
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            
            formatted_date = created_at.strftime('%d/%m/%Y %H:%M')
            
            # Format user name
            clean_user = mentioned_user.replace('@', '').title()
            
            # Truncate content jika terlalu panjang
            content = note_data.get('content', note_data.get('note_content', 'N/A'))
            if len(content) > 200:
                content = content[:197] + '...'

            # Format table source
            table_source = note_data.get('table_source', 'N/A')
            source_mapping = {
                'table_design': 'Design',
                'table_produksi': 'Produksi',
                'table_pesanan': 'Pesanan'
            }
            formatted_source = source_mapping.get(table_source, table_source)

            return {
                'notification': self.emojis['notification'],
                'note': self.emojis['note'],
                'content': self.emojis['content'],
                'user': self.emojis['user'],
                'date': self.emojis['date'],
                'id': self.emojis['id'],
                'source': self.emojis['source'],
                'urgent': self.emojis['urgent'],
                'mentioned_user': clean_user,
                'title': note_data.get('title', note_data.get('note_title', 'N/A')),
                'content_text': content,
                'created_by': note_data.get('created_by', 'N/A'),
                'formatted_date': formatted_date,
                'id_input': note_data.get('id_input', 'N/A'),
                'table_source': formatted_source
            }
            
        except Exception as e:
            logger.error(f"Error preparing note data: {str(e)}")
            return self._get_fallback_data(note_data, mentioned_user)
    
    def _clean_message(self, message: str) -> str:
        """Bersihkan pesan dari karakter yang tidak diinginkan"""
        try:
            # Remove multiple newlines
            import re
            message = re.sub(r'\n{3,}', '\n\n', message)
            
            # Remove trailing whitespace
            lines = [line.rstrip() for line in message.split('\n')]
            message = '\n'.join(lines)
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning message: {str(e)}")
            return message
    
    def _get_fallback_message(self, note_data: Dict[str, Any], mentioned_user: str) -> str:
        """Pesan fallback jika terjadi error"""
        clean_user = mentioned_user.replace('@', '').title()
        return (
            f"{self.emojis['notification']} NOTIFIKASI NOTE\n\n"
            f"Halo {clean_user},\n\n"
            f"Anda di-mention dalam note baru.\n\n"
            f"Judul: {note_data.get('note_title', 'N/A')}\n"
            f"Isi: {note_data.get('note_content', 'N/A')}\n"
            f"Dibuat oleh: {note_data.get('created_by', 'N/A')}\n\n"
            f"_Note Management System_"
        )
    
    def _get_fallback_data(self, note_data: Dict[str, Any], mentioned_user: str) -> Dict[str, str]:
        """Data fallback jika terjadi error"""
        return {
            'notification': self.emojis['notification'],
            'note': self.emojis['note'],
            'content': self.emojis['content'],
            'user': self.emojis['user'],
            'date': self.emojis['date'],
            'id': self.emojis['id'],
            'source': self.emojis['source'],
            'urgent': self.emojis['urgent'],
            'mentioned_user': mentioned_user.replace('@', '').title(),
            'title': str(note_data.get('note_title', 'N/A')),
            'content_text': str(note_data.get('note_content', 'N/A')),
            'created_by': str(note_data.get('created_by', 'N/A')),
            'formatted_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'id_input': str(note_data.get('id_input', 'N/A')),
            'table_source': str(note_data.get('table_source', 'N/A'))
        }
    
    def format_multiple_mentions(self, note_data: Dict[str, Any], 
                               mentioned_users: List[str]) -> Dict[str, str]:
        """
        Format pesan untuk multiple mentions
        
        Args:
            note_data (Dict): Data note
            mentioned_users (List): List user yang di-mention
            
        Returns:
            Dict: Dictionary dengan user sebagai key dan message sebagai value
        """
        try:
            messages = {}
            
            for user in mentioned_users:
                # Tentukan template berdasarkan konten
                template_type = self._determine_template_type(note_data)
                
                # Format pesan untuk user ini
                message = self.format_note_notification(note_data, user, template_type)
                messages[user] = message
            
            return messages
            
        except Exception as e:
            logger.error(f"Error formatting multiple mentions: {str(e)}")
            return {user: self._get_fallback_message(note_data, user) for user in mentioned_users}
    
    def _determine_template_type(self, note_data: Dict[str, Any]) -> str:
        """Tentukan jenis template berdasarkan konten note"""
        try:
            title = note_data.get('note_title', '').lower()
            content = note_data.get('note_content', '').lower()
            
            # Kata kunci untuk urgent
            urgent_keywords = ['urgent', 'segera', 'penting', 'asap', 'deadline', 'rush']
            
            # Cek apakah ada kata kunci urgent
            for keyword in urgent_keywords:
                if keyword in title or keyword in content:
                    return 'urgent_note'
            
            # Default ke note_mention
            return 'note_mention'
            
        except Exception as e:
            logger.error(f"Error determining template type: {str(e)}")
            return 'note_mention'

# Instance global untuk digunakan di module lain
message_formatter = MessageFormatter()