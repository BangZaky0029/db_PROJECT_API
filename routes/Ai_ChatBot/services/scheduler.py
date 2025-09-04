 
import schedule
import time
import logging
from ..config.wa_config import NOMER_1, NOMER_2, NOMER_3, NOMER_4, SUPERVISOR
from ..config.core.message_generator import MessageGenerator
from ..messages.message_service import send_whatsapp_message

logger = logging.getLogger(__name__)

def send_daily_messages():
    """Send daily messages to all admins"""
    try:
        msg_gen = MessageGenerator()
        
        # First send supervisor message
        supervisor_message = msg_gen.generate_supervisor_message()
        if supervisor_message:
            if send_whatsapp_message(SUPERVISOR['phone'], supervisor_message):
                logger.info(f"Supervisor message sent to {SUPERVISOR['phone']}")
                time.sleep(2)
            else:
                logger.error(f"Failed to send supervisor message to {SUPERVISOR['phone']}")
        
        # Then send individual admin messages
        admin_mapping = {
            NOMER_1: "1001",  # Lilis
            NOMER_2: "1002",  # Ina
            NOMER_3: "1003"   # Indy
        }
        
        for phone, admin_id in admin_mapping.items():
            try:
                message = msg_gen.generate_message(id_admin=admin_id)
                if message:
                    if send_whatsapp_message(phone, message):
                        logger.info(f"Message sent to {phone}")
                    else:
                        logger.error(f"Failed to send message to {phone}")
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Error processing admin {admin_id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in send_daily_messages: {str(e)}")

def start_scheduler():
    """Start the message scheduler"""
    # Schedule messages at 09:00 (morning), 13:00 (afternoon), and 20:00 (evening)
    schedule.every().day.at("09:00").do(send_daily_messages)
    schedule.every().day.at("13:00").do(send_daily_messages)
    schedule.every().day.at("22:00").do(send_daily_messages)
    
    while True:
        schedule.run_pending()
        time.sleep(60)