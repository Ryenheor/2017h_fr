import datetime as dt

def convert_date(timestamp_data):
    if timestamp_data < 0:
        return dt.datetime(1970, 1, 1) + dt.timedelta(seconds=timestamp_data)
    else:
        return dt.datetime.utcfromtimestamp(timestamp_data)

def intTryParse(value):
    try:
        res = int(value)
        return True
    except ValueError:
        return False