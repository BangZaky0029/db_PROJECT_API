 
class MessageFormatter:
    @staticmethod
    def format_status_counts(status_dict):
        """Format status counts for display"""
        return ", ".join(f"{status}={count}" for status, count in status_dict.items())

    @staticmethod
    def format_deadline_message(urgent_deadlines):
        """Format deadline message"""
        messages = []
        for item in urgent_deadlines:
            if item[2] > 0:
                messages.append(f"- Order {item[0]} (Pesanan {item[1]}) harus selesai dalam {item[2]} hari.")
            else:
                messages.append(f"- Order {item[0]} (Pesanan {item[1]}) harus selesai hari ini.")
        return "\n".join(messages) or "Tidak ada orderan mendesak."