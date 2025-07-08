# scripts/current_month_year.py

from datetime import datetime
import calendar

def get_current_month_year():
    now = datetime.now()
    month = now.month
    year = now.year
    month_name = now.strftime('%B')
    cal = calendar.monthcalendar(year, month)  # List of weeks (each is a list of 7 days)
    return month_name, year, cal

