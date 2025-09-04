from datetime import datetime
import logging
from ...services.database_service import DatabaseService
from .order_analyzer import OrderAnalyzer
from ..wa_config import NOMER_1, NOMER_2, NOMER_3, NOMER_4
from ..wa_config import ADMIN_PLATFORMS, SUPERVISOR, PLATFORM_ADMINS

logger = logging.getLogger(__name__)

class MessageGenerator:
    def __init__(self):
        self.db_service = DatabaseService()
        self.order_analyzer = OrderAnalyzer()
        # Move admin_mapping to __init__
        self.admin_mapping = {
            'Lilis': {'phone': NOMER_1, 'id': '1001'},
            'Ina': {'phone': NOMER_2, 'id': '1002'},
            'Indy': {'phone': NOMER_3, 'id': '1003'}
        }

    def generate_supervisor_message(self):
        """Generate summary message for supervisor - platform and deadline summary"""
        all_orders = self.order_analyzer.analyze_pending_by_deadline()
        
        message_parts = ["📊 REKAP TOTAL PER PLATFORM (BELUM SELESAI):"]
        
        # Group orders by platform and deadline
        platform_orders = self._group_orders_by_platform(all_orders)
        total_all_orders = 0
        total_all_qty = 0
        
        # WhatsApp section - broken down by admin
        if "WhatsApp" in platform_orders:
            message_parts.append("\n💬 WHATSAPP:")
            wa_data = platform_orders["WhatsApp"]
            
            # Process each admin separately
            for admin_name, admin_stats in wa_data['by_admin'].items():
                message_parts.append(f"\n👤 Admin {admin_name}:")
                message_parts.append(f"  Total: {admin_stats['total']} pesanan ({admin_stats['qty']} pcs)")
                
                # Group by deadline for this admin
                admin_deadline_breakdown = {}
                admin_orders = []
                
                for order in wa_data['orders']:
                    if order['nama_admin'] == admin_name:
                        admin_orders.append(order)
                        deadline = str(order['deadline'])
                        if deadline not in admin_deadline_breakdown:
                            admin_deadline_breakdown[deadline] = {
                                'total': 0,
                                'qty': 0
                            }
                        admin_deadline_breakdown[deadline]['total'] += 1
                        admin_deadline_breakdown[deadline]['qty'] += int(order['Jumlah_pcs'])
                
                # Add deadline breakdown for this admin
                if admin_deadline_breakdown:
                    message_parts.append("  Breakdown per deadline:")
                    for deadline, stats in sorted(admin_deadline_breakdown.items()):
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').strftime('%d-%m-%Y')
                        message_parts.append(f"  • {deadline_date}: {stats['total']} pesanan ({stats['qty']} pcs)")
                
                # Add order details for this admin
                if admin_orders:
                    message_parts.append("\n  📝 Detail Pesanan:")
                    for order in sorted(admin_orders, key=lambda x: str(x['deadline'])):
                        deadline_date = datetime.strptime(str(order['deadline']), '%Y-%m-%d').strftime('%d-%m-%Y')
                        # Safely get id_pesanan with fallback to '-'
                        id_pesanan = order.get('id_pesanan', '-')
                        message_parts.append(f"  • ID: {order['id_input']} | Pesanan: {id_pesanan} | Qty: {order['Jumlah_pcs']} pcs | Deadline: {deadline_date}")
                        message_parts.append(f"    Status Print: {order['status_print']} | Status Produksi: {order['status_produksi']}")
                
                # Add admin total
                message_parts.append(f"\n>> Total WhatsApp Admin {admin_name}: {admin_stats['total']} pesanan ({admin_stats['qty']} pcs)")
            
            # Add WhatsApp grand total
            message_parts.append(f"\nGrand Total WhatsApp: {wa_data['total']} pesanan ({wa_data['qty']} pcs)")
            total_all_orders += wa_data['total']
            total_all_qty += wa_data['qty']
            
            # Other marketplace platforms
            for platform in ["Shopee", "TikTok", "Tokopedia", "Lazada"]:
                if platform in platform_orders:
                    data = platform_orders[platform]
                    total_all_orders += data['total']
                    total_all_qty += data['qty']
                    
                    message_parts.append(f"\n🔸 {platform}:")
                    message_parts.append(f"  Total: {data['total']} pesanan ({data['qty']} pcs)")
                    
                    # Group by deadline for this platform
                    deadline_breakdown = {}
                    for order in data['orders']:
                        deadline = str(order['deadline'])
                        if deadline not in deadline_breakdown:
                            deadline_breakdown[deadline] = {
                                'total': 0,
                                'qty': 0
                            }
                        deadline_breakdown[deadline]['total'] += 1
                        deadline_breakdown[deadline]['qty'] += int(order['Jumlah_pcs'])
                    
                    # Add deadline breakdown
                    if deadline_breakdown:
                        message_parts.append("  Breakdown per deadline:")
                        for deadline, stats in sorted(deadline_breakdown.items()):
                            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').strftime('%d-%m-%Y')
                            message_parts.append(f"  • {deadline_date}: {stats['total']} pesanan ({stats['qty']} pcs)")
                    
                    # Add order details for this platform
                    if data['orders']:
                        message_parts.append("\n  📝 Detail Pesanan:")
                        for order in sorted(data['orders'], key=lambda x: str(x['deadline'])):
                            deadline_date = datetime.strptime(str(order['deadline']), '%Y-%m-%d').strftime('%d-%m-%Y')
                            # Safely get id_pesanan with fallback to '-'
                            id_pesanan = order.get('id_pesanan', '-')
                            message_parts.append(f"  • ID: {order['id_input']} | Pesanan: {id_pesanan} | Qty: {order['Jumlah_pcs']} pcs | Deadline: {deadline_date}")
                            message_parts.append(f"    Status Print: {order['status_print']} | Status Produksi: {order['status_produksi']}")
        
            # Add total summary
            message_parts.append(f"\n\n📈 TOTAL KESELURUHAN Platform:")
            message_parts.append(f"* Total Pesanan: {total_all_orders}")
            message_parts.append(f"* Total Quantity: {total_all_qty} pcs")
            
            # Add timestamp
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            message_parts.append(f"\n\nTimestamp Pengiriman pesan: {current_time}")
            message_parts.append("> Sent via fonnte.com")
            
            return "\n".join(message_parts)

    def generate_order_ids_message(self):
        """Generate message with order IDs grouped by platform and admin"""
        all_orders = self.order_analyzer.analyze_pending_by_deadline()
        
        message_parts = ["📋 DAFTAR ID PESANAN PENDING:"]
        
        # Group orders by platform and deadline
        platform_orders = self._group_orders_by_platform(all_orders)
        total_all_orders = 0
        
        # WhatsApp section - broken down by admin
        if "WhatsApp" in platform_orders:
            message_parts.append("\n💬 WHATSAPP:")
            wa_data = platform_orders["WhatsApp"]
            
            # Process each admin separately
            for admin_name, admin_stats in wa_data['by_admin'].items():
                message_parts.append(f"\n👤 Admin {admin_name}: ({admin_stats['total']} pesanan)")
                
                # Group by deadline for this admin
                admin_orders_by_deadline = {}
                for order in wa_data['orders']:
                    if order['nama_admin'] == admin_name:
                        deadline = str(order['deadline'])
                        if deadline not in admin_orders_by_deadline:
                            admin_orders_by_deadline[deadline] = []
                        admin_orders_by_deadline[deadline].append(order)
                
                # List order IDs by deadline
                for deadline, orders in sorted(admin_orders_by_deadline.items()):
                    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').strftime('%d-%m-%Y')
                    message_parts.append(f"  📅 Deadline {deadline_date}: ({len(orders)} pesanan)")
                    
                    # List all order IDs for this deadline
                    order_ids = [f"{order['id_input']} ({order['Jumlah_pcs']} pcs)" for order in orders]
                    message_parts.append("  " + ", ".join(order_ids))
                
                total_all_orders += wa_data['total']
            
        # Other marketplace platforms
        for platform in ["Shopee", "TikTok", "Tokopedia", "Lazada"]:
            if platform in platform_orders:
                data = platform_orders[platform]
                message_parts.append(f"\n🔸 {platform}: ({data['total']} pesanan)")
                
                # Group by deadline
                platform_orders_by_deadline = {}
                for order in data['orders']:
                    deadline = str(order['deadline'])
                    if deadline not in platform_orders_by_deadline:
                        platform_orders_by_deadline[deadline] = []
                    platform_orders_by_deadline[deadline].append(order)
                
                # List order IDs by deadline
                for deadline, orders in sorted(platform_orders_by_deadline.items()):
                    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').strftime('%d-%m-%Y')
                    message_parts.append(f"  📅 Deadline {deadline_date}: ({len(orders)} pesanan)")
                    
                    # List all order IDs for this deadline
                    order_ids = [f"{order['id_input']} ({order['Jumlah_pcs']} pcs)" for order in orders]
                    message_parts.append("  " + ", ".join(order_ids))
                
                total_all_orders += data['total']
            
        # Add total summary
        message_parts.append(f"\n\n📈 TOTAL KESELURUHAN:")
        message_parts.append(f"* Total Pesanan: {total_all_orders}")
        
        # Add timestamp
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        message_parts.append(f"\n\nTimestamp Pengiriman pesan: {current_time}")
        message_parts.append("> Sent via fonnte.com")
        
        return "\n".join(message_parts)

    def generate_message(self, id_admin=None, include_ids=False):
        """Generate formatted message for pending orders"""
        try:
            # Choose which message format to use
            if include_ids:
                return self.generate_order_ids_message()
            else:
                return self.generate_supervisor_message()
        except Exception as e:
            logger.error(f"Error generating message: {str(e)}")
            raise ValueError(f"Failed to generate message: {str(e)}")

    def _group_orders_by_platform(self, all_orders):
        """Helper method to group orders by platform"""
        platform_orders = {}
        
        for deadline_group in all_orders.values():
            for order in deadline_group['orders']:
                platform = order['platform']
                if platform not in platform_orders:
                    platform_orders[platform] = {
                        'total': 0,
                        'qty': 0,
                        'by_admin': {},
                        'orders': []
                    }
                
                platform_orders[platform]['orders'].append(order)
                platform_orders[platform]['total'] += 1
                platform_orders[platform]['qty'] += int(order['Jumlah_pcs'])
                
                if platform == "WhatsApp":
                    admin_name = order['nama_admin']
                    if admin_name not in platform_orders[platform]['by_admin']:
                        platform_orders[platform]['by_admin'][admin_name] = {
                            'total': 0,
                            'qty': 0
                        }
                    platform_orders[platform]['by_admin'][admin_name]['total'] += 1
                    platform_orders[platform]['by_admin'][admin_name]['qty'] += int(order['Jumlah_pcs'])
    
        return platform_orders