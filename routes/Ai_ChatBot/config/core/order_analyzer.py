from datetime import datetime
from project_api.routes.Ai_ChatBot.services.database_service import DatabaseService
from project_api.routes.Ai_ChatBot.utils.date_utils import DateUtils

class OrderAnalyzer:
    def __init__(self):
        self.db_service = DatabaseService()
        self.data = self.db_service.get_pending_orders()
        self.all_orders = [item for item in self.data]
        self.total_orders = len(self.all_orders)
        self.total_qty = sum(int(item['Jumlah_pcs']) for item in self.all_orders)

    def analyze_platform_data(self, platform_name, id_admin=None):
        """Analyze orders for specific platform and admin"""
        if id_admin:
            # Convert id_admin to string for comparison if needed
            admin_id = str(id_admin)
            platform_orders = [item for item in self.data 
                              if item['platform'] == platform_name 
                              and str(item['id_admin']) == admin_id]
        else:
            platform_orders = [item for item in self.data if item['platform'] == platform_name]
        
        return self._calculate_platform_metrics(platform_orders, platform_name)

    def _calculate_platform_metrics(self, platform_orders, platform_name):
        """Calculate metrics for platform orders"""
        total_qty = sum(int(item['Jumlah_pcs']) for item in platform_orders)
        orders_by_id = {}
        status_count = {'EDITING': 0, '-': 0}
        produksi_count = {'EDITING': 0, '-': 0}

        for order in platform_orders:
            order_id = order['id_input']
            if order_id not in orders_by_id:
                orders_by_id[order_id] = 0
            orders_by_id[order_id] += int(order['Jumlah_pcs'])
            
            status_count[order['status_print']] = status_count.get(order['status_print'], 0) + 1
            produksi_count[order['status_produksi']] = produksi_count.get(order['status_produksi'], 0) + 1

        urgent_deadlines = self._get_urgent_deadlines(platform_orders)
        
        return {
            'platform': platform_name,
            'total_orders': len(platform_orders),
            'unique_pesanan': len(orders_by_id),
            'total_qty': total_qty,
            'qty_by_pesanan': orders_by_id,
            'urgent_deadlines': urgent_deadlines,
            'status_print': status_count,
            'status_produksi': produksi_count,
            'orders': platform_orders  # Include full order details
        }

    def _get_urgent_deadlines(self, orders):
        """Get orders with urgent deadlines (≤ 2 days)"""
        today = datetime.now().date()
        urgent_deadlines = []
        for order in orders:
            deadline = datetime.strptime(str(order['deadline']), '%Y-%m-%d').date()
            days_remaining = (deadline - today).days
            if days_remaining <= 2:
                urgent_deadlines.append({
                    'id_input': order['id_input'],
                    'nama_produk': order['nama_produk'],
                    'days_remaining': days_remaining,
                    'link_foto': order['link_foto']
                })
        return urgent_deadlines

    def get_orders_by_admin(self, id_admin):
        """Get all orders for a specific admin with full details"""
        admin_id = str(id_admin)
        admin_orders = [item for item in self.data if str(item['id_admin']) == admin_id]
        
        # Group by platform
        platforms = {}
        for order in admin_orders:
            platform = order['platform']
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(order)
            
        return {
            'total_orders': len(admin_orders),
            'total_qty': sum(int(item['Jumlah_pcs']) for item in admin_orders),
            'platforms': platforms,
            'orders_by_deadline': self._group_by_deadline(admin_orders)
        }
        
    def _group_by_deadline(self, orders):
        """Group orders by deadline date"""
        deadline_groups = {}
        
        for order in orders:
            deadline_str = str(order['deadline'])
            if deadline_str not in deadline_groups:
                deadline_groups[deadline_str] = []
            
            deadline_groups[deadline_str].append(order)
            
        return deadline_groups

    def analyze_products(self):
        """Analyze product statistics"""
        product_stats = {}
        deadline_stats = {}
        
        for order in self.data:
            product_name = order['nama_produk']
            qty = int(order['Jumlah_pcs'])
            
            # Update product stats
            if product_name not in product_stats:
                product_stats[product_name] = {
                    'total_qty': 0,
                    'orders': []
                }
            product_stats[product_name]['total_qty'] += qty
            product_stats[product_name]['orders'].append(order)
            
            # Update deadline stats
            deadline_str = str(order['deadline'])
            if deadline_str not in deadline_stats:
                deadline_stats[deadline_str] = {'total_qty': 0, 'products': {}}
            
            deadline_stats[deadline_str]['total_qty'] += qty
            if product_name not in deadline_stats[deadline_str]['products']:
                deadline_stats[deadline_str]['products'][product_name] = {
                    'qty': 0,
                    'orders': []
                }
            deadline_stats[deadline_str]['products'][product_name]['qty'] += qty
            deadline_stats[deadline_str]['products'][product_name]['orders'].append(order)

        return {'product_stats': product_stats, 'deadline_stats': deadline_stats}

    def analyze_pending_by_deadline(self):
        """Analyze pending orders grouped by deadline"""
        deadline_groups = {}
        
        for order in self.data:
            deadline_str = str(order['deadline'])
            
            if deadline_str not in deadline_groups:
                deadline_groups[deadline_str] = {
                    'total_pending': 0,
                    'pending_print': 0,
                    'pending_produksi': 0,
                    'orders': []
                }
            
            group = deadline_groups[deadline_str]
            if order['status_print'] == '-':
                group['pending_print'] += 1
            if order['status_produksi'] == '-':
                group['pending_produksi'] += 1
            group['total_pending'] = max(group['pending_print'], group['pending_produksi'])
            
            group['orders'].append(order)
        
        return deadline_groups
        
    def generate_admin_message(self, id_admin):
        """Generate a formatted message for a specific admin"""
        admin_id = str(id_admin)
        admin_data = self.get_orders_by_admin(admin_id)
        
        if admin_data['total_orders'] == 0:
            return "✅ Tidak ada pesanan pending saat ini."
            
        # Format the message
        message_parts = [f"📋 RINGKASAN PESANAN PENDING ({admin_data['total_orders']} pesanan)"]
        
        # Group by deadline
        for deadline, orders in sorted(admin_data['orders_by_deadline'].items()):
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').strftime('%d-%m-%Y')
            message_parts.append(f"\n📅 DEADLINE: {deadline_date} ({len(orders)} pesanan)")
            
            # Group by platform within each deadline
            platform_orders = {}
            for order in orders:
                platform = order['platform']
                if platform not in platform_orders:
                    platform_orders[platform] = []
                platform_orders[platform].append(order)
            
            # Add platform sections
            for platform, p_orders in platform_orders.items():
                message_parts.append(f"\n🔹 Platform: {platform} ({len(p_orders)} pesanan)")
                
                for order in p_orders:
                    status_print = "✅" if order['status_print'] != '-' else "❌"
                    status_produksi = "✅" if order['status_produksi'] != '-' else "❌"
                    
                    message_parts.append(f"• ID: {order['id_input']} - {order['nama_produk']}")
                    message_parts.append(f"  Jumlah: {order['Jumlah_pcs']} pcs")
                    message_parts.append(f"  Status: Print {status_print} | Produksi {status_produksi}")
                    if order['link_foto']:
                        message_parts.append(f"  Foto: {order['link_foto']}")
                    message_parts.append("")
        
        # Add urgent orders section
        urgent_orders = []
        for deadline, orders in admin_data['orders_by_deadline'].items():
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            days_remaining = (deadline_date - datetime.now().date()).days
            
            if days_remaining <= 2:
                for order in orders:
                    urgent_orders.append({
                        'id_input': order['id_input'],
                        'nama_produk': order['nama_produk'],
                        'days': days_remaining,
                        'deadline': deadline_date.strftime('%d-%m-%Y')
                    })
        
        if urgent_orders:
            message_parts.append("\n⚠️ PESANAN URGENT:")
            for order in urgent_orders:
                days_text = "hari ini" if order['days'] == 0 else f"{order['days']} hari lagi"
                message_parts.append(f"• ID: {order['id_input']} - {order['nama_produk']}")
                message_parts.append(f"  Deadline: {order['deadline']} ({days_text})")
        
        # Add platform summary section
        message_parts.append("\n📊 REKAP TOTAL PER PLATFORM:")
        platform_summary = {}
        for platform, orders in admin_data['platforms'].items():
            total_qty = sum(int(order['Jumlah_pcs']) for order in orders)
            platform_summary[platform] = {
                'total_orders': len(orders),
                'total_qty': total_qty,
                'by_deadline': {}
            }
            
            # Group by deadline within platform
            for order in orders:
                deadline_str = str(order['deadline'])
                deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').strftime('%d-%m-%Y')
                if deadline_date not in platform_summary[platform]['by_deadline']:
                    platform_summary[platform]['by_deadline'][deadline_date] = {
                        'orders': 0,
                        'qty': 0
                    }
                platform_summary[platform]['by_deadline'][deadline_date]['orders'] += 1
                platform_summary[platform]['by_deadline'][deadline_date]['qty'] += int(order['Jumlah_pcs'])

        # Add summary to message
        for platform, summary in platform_summary.items():
            message_parts.append(f"\n🔸 {platform}:")
            message_parts.append(f"  Total: {summary['total_orders']} pesanan ({summary['total_qty']} pcs)")
            message_parts.append("  Breakdown per deadline:")
            for deadline, stats in sorted(summary['by_deadline'].items()):
                message_parts.append(f"  • {deadline}: {stats['orders']} pesanan ({stats['qty']} pcs)")

        # Add grand total
        message_parts.append(f"\n📈 TOTAL KESELURUHAN:")
        message_parts.append(f"• Total Pesanan: {admin_data['total_orders']}")
        message_parts.append(f"• Total Quantity: {admin_data['total_qty']} pcs")
        
        return "\n".join(message_parts)