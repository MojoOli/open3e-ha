from enum import StrEnum
from datetime import datetime


class LegionellaProtectionWeekday(StrEnum):
    Monday = "monday"
    Tuesday = "tuesday"
    Wednesday = "wednesday"
    Thursday = "thursday"
    Friday = "friday"
    Saturday = "saturday"
    Sunday = "sunday" 


@staticmethod
def get_lp_weekday(wday: int):
    match wday:
        case 0:
            return LegionellaProtectionWeekday.Monday
        case 1:
            return LegionellaProtectionWeekday.Tuesday
        case 2:
            return LegionellaProtectionWeekday.Wednesday
        case 3:
            return LegionellaProtectionWeekday.Thursday
        case 4:
            return LegionellaProtectionWeekday.Friday
        case 5:
            return LegionellaProtectionWeekday.Saturday
        case 6:
            return LegionellaProtectionWeekday.Sunday
    return None

# for future purposes, currently not used in code
#@staticmethod
#def ConcStrLPWeekDay(WeekdayInt: int, Starttime: datetime) -> str:
#    match WeekdayInt:
#        case 0:
#            Weekday = "Montag"
#        case 1:
#            Weekday = "Dienstag"
#        case 2:
#            Weekday = "Mittwoch"
#        case 3:
#            Weekday = "Donnerstag"
#        case 4:
#            Weekday = "Freitag"
#        case 5:
#            Weekday = "Samstag"
#        case 6:
#            Weekday = "Sonntag"
#    try:
#        return Weekday + " um " + Starttime.strftime("%H:%M")
#    except ValueError:  # If dt_strinput did not match the format
#        return '-'
