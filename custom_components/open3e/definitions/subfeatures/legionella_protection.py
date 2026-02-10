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

