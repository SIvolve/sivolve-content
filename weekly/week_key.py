"""SIvolve publication weeks use Victorian local dates (including DST)."""
from datetime import datetime
from zoneinfo import ZoneInfo
MELBOURNE = ZoneInfo('Australia/Melbourne')
def current_week_key(now=None):
    now = now or datetime.now(MELBOURNE)
    date = now.astimezone(MELBOURNE)
    year, week, _ = date.isocalendar()
    return f'{year}-W{week:02d}'
def melbourne_monday(now=None):
    now = now or datetime.now(MELBOURNE)
    return now.astimezone(MELBOURNE).weekday() == 0
