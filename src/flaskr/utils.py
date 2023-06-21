from datetime import datetime, date, time


def getDateFromString(string: str) -> date:
    return datetime.strptime(string, "%Y-%m-%d").date()

def getStringFromDate(date: date) -> str:
    return date.strftime("%Y-%m-%d")

def getTimeFromString(string: str) -> time:
    return datetime.strptime(string, "%H:%M").time()

def getStringFromTime(time: time) -> str:
    return time.strftime("%H:%M")