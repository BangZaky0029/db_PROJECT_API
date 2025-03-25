 
from datetime import datetime

class DateUtils:
    @staticmethod
    def get_days_remaining(deadline_str):
        """Calculate days remaining until deadline"""
        today = datetime.now().date()
        deadline = datetime.strptime(str(deadline_str), '%Y-%m-%d').date()
        return (deadline - today).days

    @staticmethod
    def format_deadline_text(days_remaining):
        """Format deadline text based on days remaining"""
        if days_remaining == 0:
            return "Hari Ini"
        elif days_remaining == 1:
            return "Besok"
        elif days_remaining == 2:
            return "Lusa"
        else:
            return f"{days_remaining} hari lagi"