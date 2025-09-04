 
from datetime import datetime
from ..config.wa_config import (
    API_KEY, NOMER_1, NOMER_2, NOMER_3, NOMER_4,
    ADMIN_PLATFORMS, SUPERVISOR, PLATFORM_ADMINS
)
from ..config.core.order_analyzer import OrderAnalyzer
from ..config.core.message_generator import MessageGenerator
from ..services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

def create_messages():
    """Main function to create all messages"""
    try:
        # Initialize services
        db_service = DatabaseService()
        analyzer = OrderAnalyzer()
        message_gen = MessageGenerator()
        
        # Get pending orders from database
        pending_orders = db_service.get_pending_orders()
        
        if not pending_orders:
            logger.info("No pending orders found")
            return None
            
        messages = {}
        
        # Generate messages for each admin
        for admin_name, admin_info in ADMIN_PLATFORMS.items():
            try:
                message = message_gen.generate_message(id_admin=admin_info['id'])
                if message:
                    messages[admin_info['phone']] = message
                    logger.info(f"Generated message for {admin_name}")
            except Exception as e:
                logger.error(f"Error generating message for {admin_name}: {str(e)}")
                continue
        
        # Generate supervisor summary message
        try:
            supervisor_message = message_gen.generate_supervisor_message()
            if supervisor_message:
                messages[SUPERVISOR['phone']] = supervisor_message
                logger.info("Generated supervisor summary message")
        except Exception as e:
            logger.error(f"Error generating supervisor message: {str(e)}")
        
        return messages if messages else None
        
    except Exception as e:
        logger.error(f"Error in create_messages: {str(e)}")
        raise