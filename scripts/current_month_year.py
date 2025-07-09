# scripts/current_month_year.py

from datetime import datetime
import calendar

def get_current_month_year():
    now = datetime.now()
    month_num = now.month
    month_name = now.strftime('%B')
    year = now.year
    cal = calendar.monthcalendar(year, month_num)
    return month_name, year, cal, month_num

