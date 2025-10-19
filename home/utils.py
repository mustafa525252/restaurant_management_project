
from datetime import datetime, time

OPENING_HOURS = {
    'Monday':(time(9, 0), time(22, 0)),
    'Tuesday':(time(9, 0), time(22, 0)),
    'Wednesday':(time(9, 0), time(22, 0)),
    'Thursday':(time(9, 0), time(22, 0)),
    'Friday':(time(9, 0), time(23, 0)),
    'Saturday':(time(9, 0), time(23, 0)),
    'Sunday':(time(9, 0), time(21, 0)),
}

def is_restaurant_open():
    now = datetime.now()
    current_day = now.strftime('%A')
    current_time = now.time()

    hours = OPENING_HOURS.get(current_day)

    if not hours:
        return False

    open_time, close_time = hours
    return open_time <= current_time <= close_time