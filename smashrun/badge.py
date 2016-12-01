# vim: ft=python expandtab softtabstop=0 tabstop=4 shiftwidth=4

import copy
import dateutil
import logging
import math
import sys
from datetime import datetime
from datetime import timedelta
from dateutil.tz import tzoffset
from pint import UnitRegistry

UNITS = UnitRegistry()

def srdate_to_datetime(datestring, utc=False):
    # 2016-11-17T07:11:00-08:00

    if utc:
        dt = datestring
        fmt = '%Y-%m-%dT%H:%M:%S.%f'
        to_zone = dateutil.tz.tzlocal()
    else:
        dt = datestring[:-6]
        tz = datestring[-6:]
        fmt = '%Y-%m-%dT%H:%M:%S'
        offset = (int(tz[1:3]) * 60 * 60) + (int(tz[4:6]) * 60)
        if tz[0] == '-':
            offset = -offset
        to_zone = tzoffset(None, offset)

    result = datetime.strptime(dt, fmt)
    return result.replace(tzinfo=to_zone)


def sr_get_records(activity, key):
    idx = -1
    for k in activity['recordingKeys']:
        idx += 1
        if activity['recordingKeys'][idx] == key:
            break
    assert idx in range(len(activity['recordingKeys'])), "Unable to find valid index in %s for '%s'" % (activity['recordingKeys'], key)
    return activity['recordingValues'][idx]


def sr_elevation_delta(activity):
    elevations = sr_get_records(activity, 'elevation')
    min_elevation = sys.maxsize
    max_elevation = -sys.maxsize
    for elevation in elevations:
        min_elevation = min(elevation, min_elevation)
        max_elevation = max(elevation, max_elevation)

    return (max_elevation - min_elevation) * UNITS.meters

def avg_pace(activity, distance_unit=UNITS.mile, time_unit=UNITS.minute):
    distance = activity['distance'] * UNITS.kilometer
    time = activity['duration'] * UNITS.second
    return (time.to(time_unit) / distance.to(distance_unit)).magnitude


def sr_pace_variability(activity):
    distance = sr_get_records(activity, 'distance')
    time = sr_get_records(activity, 'clock')
    assert len(distance) == len(time), "Distance and time records should be the same length, but they aren't for activity %s" % (activity['activityId'])

    paces = []  # This will be in km/s
    for i in range(1, len(distance)):
        d = distance[i] - distance[i-1]
        t = time[i] - time[i-1]
        paces.append(d / t)

    def calc_mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)

    # Determine the mean
    mean = calc_mean(paces)
    squares = []
    for p in paces:
        squares.append((p - mean) ** 2)

    variance = calc_mean(squares)
    std_dev = math.sqrt(variance)

def is_different_year(d1, d2):
    if d1 is None or d2 is None:
        return True
    elif d1.year != d2.year:
        return True
    else:
        return False

def is_different_month(d1, d2):
    if d1 is None or d2 is None:
        return True
    elif d1.month != d2.month:
        return True
    elif d1.year != d2.year:
        return True
    else:
        return False

class BadgeSet(object):
    def __init__(self, start_date, only_ids=[]):
        self.start_date = start_date

        self._badges = {}
        self._badges[1] = EarlyBird()
        self._badges[2] = NightOwl()
        self._badges[3] = LunchHour()
        self._badges[4] = Popular()
        self._badges[5] = OCD()
        self._badges[6] = OneMile()
        self._badges[7] = Marathoner()
        self._badges[8] = UltraMarathoner()
        self._badges[9] = HalfMarathoner()
        self._badges[10] = TenKer()
        self._badges[11] = BeatA9YearOld()
        self._badges[12] = PoundedPalin()
        self._badges[13] = PastDiddy()
        self._badges[14] = UnderOprah()
        self._badges[15] = ClearedKate()
        self._badges[16] = FiveForFive()
        self._badges[17] = TenForTen()
        self._badges[18] = TwentyForTwenty()
        self._badges[19] = FiftyForFifty()
        self._badges[20] = Perfect100()
        self._badges[21] = TenUnderYourBelt()
        self._badges[22] = TwentyUnderYourBelt()
        self._badges[23] = FiftyUnderYourBelt()
        self._badges[24] = ACenturyDown()
        self._badges[25] = Monster500()
        self._badges[26] = SolidWeek()
        self._badges[27] = RockedTheWeek()
        self._badges[28] = SolidMonth()
        self._badges[29] = RockedTheMonth()
        self._badges[30] = RunNutMonth()
        self._badges[31] = Veteran()
        self._badges[32] = GuineaPig()
        self._badges[33] = FiveKer()
        self._badges[34] = BirthdayRun()
        self._badges[35] = Corleone()
        self._badges[36] = BroughtABuddy()
        self._badges[37] = GotFriends()
        self._badges[38] = SocialSeven()
        self._badges[39] = SharesWell()
        self._badges[40] = PackLeader()
        self._badges[101] = NYCPhilly()
        self._badges[102] = LondonParis()
        self._badges[103] = SydneyMelbourne()
        self._badges[104] = NYCChicago()
        self._badges[105] = MiamiToronto()
        self._badges[106] = ChariotsOfFire()
        self._badges[107] = WentToWork()
        self._badges[108] = ThatsADay()
        self._badges[109] = WeekNotWeak()
        self._badges[110] = OutlastTheAlamo()
        self._badges[111] = ChillRunner()
        self._badges[112] = EasyRunner()
        self._badges[113] = RoadRunner()
        self._badges[114] = Mercury()
        self._badges[115] = FastAndSlow()
        self._badges[126] = Stairs()
        self._badges[127] = SteepStairs()
        self._badges[128] = LongStairs()
        self._badges[129] = LongSteepStairs()
        self._badges[130] = ToweringStairs()
        self._badges[131] = InItForJanuary()
        self._badges[132] = InItForFebruary()
        self._badges[133] = InItForMarch()
        self._badges[134] = InItForApril()
        self._badges[135] = InItForMay()
        self._badges[136] = InItForJune()
        self._badges[137] = InItForJuly()
        self._badges[138] = InItForAugust()
        self._badges[139] = InItForSeptember()
        self._badges[140] = InItForOctober()
        self._badges[141] = InItForNovember()
        self._badges[142] = InItForDecember()
        self._badges[143] = ColorPicker()
        self._badges[144] = ThreeSixtyFiveDays()
        # self._badges[145] = ThreeSixtyFiveOf760()
        self._badges[146] = ThreeSixtyFiveOf365()
        #self._badges[147] = AYearInRunning()
        #self._badges[148] = LeapYearSweep()
        self._badges[149] = SmashrunForLife()
        self._badges[150] = Translator()
        #self._badges[151] = UltraUltra100k() ???
        #self._badges[201] = USofR()
        #self._badges[202] = International()
        #self._badges[203] = TopAndBottom()
        #self._badges[204] = FourCorners()
        #self._badges[205] = InternationalSuperRunner()
        #self._badges[206] = SpecialAgent()
        #self._badges[207] = NCAAFitnessTest() ???
        #self._badges[208] = CooperTest2800m() ???
        #self._badges[209] = SuperAgent()
        #self._badges[210] = ArmyRanger() ???
        #self._badges[211] = FastStart5k() ???
        #self._badges[212] = FastFinish5k() ???
        #self._badges[213] = FastMiddle10k() ???
        #self._badges[214] = FastStartAndFinish5k() ???
        #self._badges[215] = SuperFastStart5k() ???
        #self._badges[216] = Sunriser()
        #self._badges[217] = FullMoonRunner()
        #self._badges[218] = Sunsetter()
        #self._badges[219] = LongestDay()
        #self._badges[220] = ShortestDay()
        self._badges[221] = FourFurther()
        self._badges[222] = SixFurther()
        self._badges[223] = FourFarFurther()
        self._badges[224] = SixFarFurther()
        self._badges[225] = FurtherToFarther()
        # self._badges[226] = ShortAndSteady()
        # self._badges[227] = LongAndSteady()
        # self._badges[228] = ShortAndSolid()
        # self._badges[229] = LongAndSolid()
        # self._badges[230] = LongAndRockSolid()
        # self._badges[231] = TwoBy33()
        # self._badges[232] = TwoBy99()
        # self._badges[233] = TwoBy33By10k()
        # self._badges[234] = TwoBy99By5k()
        # self._badges[235] = TwoBy365By10k()
        self._badges[236] = TopOfTable()
        self._badges[237] = ClimbedHalfDome()
        self._badges[238] = ReachedFitzRoy()
        self._badges[239] = MatterhornMaster()
        self._badges[240] = ConqueredEverest()
        self._badges[241] = ToweredPisa()
        self._badges[242] = TopOfWashington()
        self._badges[243] = OverTheEiffel()
        self._badges[244] = AboveTheBurj()
        self._badges[245] = ToPikesPeak()

        if len(only_ids):
            keys_to_del = [x for x in self._badges.keys() if x not in only_ids]
            for key in keys_to_del:
                del self._badges[key]

    @property
    def badges(self):
        return self._badges.values()

    def add_user_info(self, info):
        logging.debug("Adding user info for ID=%s %s" % (info['id'], info['name']))
        if info['id'] not in self._badges:
            logging.warning("Not adding user info for badge. Not implemented yet")
        else:
            self._badges[info['id']].add_user_info(info)

    def add_activity(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        if self.start_date is None or start_date >= self.start_date:
            logging.debug("Adding activity %s" % (activity['activityId']))
            for b in self.badges:
                b.add_activity(activity)
        else:
            logging.debug("Skipping activity %s that occured before %s" % (activity['activityId'], self.start_date))


class Badge(object):
    def __init__(self, name):
        self.activityId = None
        self.actualEarnedDate = None
        self.info = {}
        self.name = name

    def add_user_info(self, info):
        self.info = copy.copy(info)

    # activity is a hash containing the activity info as received from Smashrun
    def add_activity(self, activity):
        raise NotImplementedError("subclasses must implement add_activity")

    def acquire(self, activity):
        # Only allow badges to be acquired once -- Smashrun doesn't have levels (YET!)
        if self.acquired:
            return

        if self.activityId is None:
            self.activityId = activity['activityId']
            self.actualEarnedDate = srdate_to_datetime(activity['startDateTimeLocal'])
            logging.info("%s: acquired from activity %s on %s" % (self.name, self.activityId, self.actualEarnedDate))

    @property
    def acquired(self):
        if self.activityId is not None or self.actualEarnedDate is not None:
            return True
        else:
            return False

    def __get_info(self, key):
        if key not in self.info:
            raise RuntimeError("Must add user info before accessing '%s'"
                               % (key))
        return self.info[key]


##################################################################
#
# Badges that require N number of some sort of criteria. Criteria
# may reset and thus a reset method is provided
#
##################################################################
class CountingBadge(Badge):
    def __init__(self, name, limit, reset=0):
        super(CountingBadge, self).__init__(name)
        self.limit = limit
        self._reset = reset
        self.reset(log=False)

    def add_activity(self, activity):
        # Do this in two steps. increment() may invoke reset()
        delta = self.increment(activity)
        self.count += delta
        description = '[ID=%s START=%s DIST=%smi AVGPACE=%smin/mi ELEV=%s\']' % (activity['activityId'],
                                                                                 srdate_to_datetime(activity['startDateTimeLocal']).strftime('%Y-%m-%d %H:%M'),
                                                                                 (activity['distance'] * UNITS.kilometer).to(UNITS.mile).magnitude,
                                                                                 avg_pace(activity, distance_unit=UNITS.mile, time_unit=UNITS.minutes),
                                                                                 '?')
        logging.debug("%s: %s run qualifies. count now %s" % (self.name, description, self.count))
        if not self.acquired:
            if self.count >= self.limit:
                self.acquire(activity)

    def reset(self, log=True):
        self.count = self._reset
        if log:
            logging.debug("%s resetting count to %s" % (self.name, self.count))

    def increment(self, activity):
        raise NotImplementedError("subclasses must implement increment")


##################################################################
#
# A counting badge that will use units from the pint package
#
##################################################################
class CountingUnitsBadge(CountingBadge):
    def __init__(self, name, limit, units, reset=0):
        super(CountingUnitsBadge, self).__init__(name, limit * units, reset * units)


##################################################################
#
# Total time badges
#
##################################################################
class TotalTimeBadge(CountingUnitsBadge):
    def __init__(self, name, limit, units=UNITS.hours):
        super(TotalTimeBadge, self).__init__(name, limit, units)

    def increment(self, activity):
        return activity['duration'] * UNITS.seconds

class ChariotsOfFire(TotalTimeBadge):
    def __init__(self):
        super(ChariotsOfFire, self).__init__('Chariots of Fire', 124, units=UNITS.minutes)

class WentToWork(TotalTimeBadge):
    def __init__(self):
        super(WentToWork, self).__init__('Went to work', 8)

class ThatsADay(TotalTimeBadge):
    def __init__(self):
        super(ThatsADay, self).__init__('That\'s a day', 24)

class WeekNotWeak(TotalTimeBadge):
    def __init__(self):
        super(WeekNotWeak, self).__init__('Week not weak', 168)

class OutlastTheAlamo(TotalTimeBadge):
    def __init__(self):
        super(OutlastTheAlamo, self).__init__('Outlast the Alamo', 312)

class ThreeSixtyFiveDays(TotalTimeBadge):
    def __init__(self):
        super(ThreeSixtyFiveDays, self).__init__('365 days', 365, units=UNITS.day)


##################################################################
#
# Misc counting badges
#
##################################################################
class EarlyBird(CountingUnitsBadge):
    def __init__(self):
        super(EarlyBird, self).__init__('Early Bird', 10, UNITS.day)

    def increment(self, activity):
        # FIXME: What if there are 2 runs before 7 on a given day?
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        sevenAM = start_date.replace(hour=7, minute=0, second=0)

        if start_date <= sevenAM:
            return 1 * UNITS.day
        return 0 * UNITS.day


class NightOwl(CountingUnitsBadge):
    def __init__(self):
        super(NightOwl, self).__init__('Night Owl', 10, units=UNITS.day)

    def increment(self, activity):
        # FIXME: What if there are 2 runs after 9 on a given day?
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        end_date = start_date + timedelta(seconds=activity['duration'])
        ninePM = end_date.replace(hour=21, minute=0, second=0)

        if end_date >= ninePM:
            return 1 * UNITS.day
        return 0 * UNITS.day

class LunchHour(CountingUnitsBadge):
    def __init__(self):
        super(LunchHour, self).__init__('Lunch Hour', 10, units=UNITS.day)

    def increment(self, activity):
        # FIXME: What if there are 2 runs during lunch on a given day?
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])

        is_weekday = start_date.weekday() in range(0, 6) # Mon-Fri
        noon = start_date.replace(hour=12, minute=0, second=0)
        twoPM = start_date.replace(hour=14, minute=0, second=0)

        if is_weekday and start_date >= noon and start_date <= twoPM:
            return 1 * UNITS.day
        return 0 * UNITS.day

##################################################################
#
# Badges that require a running streak (consecutive days)
#
##################################################################
class RunStreakBadge(CountingUnitsBadge):
    def __init__(self, name, limit, units=UNITS.day):
        super(RunStreakBadge, self).__init__(name, limit, units)
        self.datetime_of_lastrun = None

    # FIXME: this currently allows double counting of multiple runs on the same day
    def increment(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])

        streak_broken = False
        if self.datetime_of_lastrun is not None:
            delta = start_date - self.datetime_of_lastrun
            streak_broken = delta.days > 1 or (delta.days == 1 and (delta.seconds > 0 or delta.microseconds > 0))

        if streak_broken:
            self.reset()

        self.datetime_of_lastrun = start_date
        return 1 * UNITS.day

class OneMile(RunStreakBadge):
    def __init__(self):
        super(OneMile, self).__init__('One Mile', 1)

class FiveForFive(RunStreakBadge):
    def __init__(self):
        super(FiveForFive, self).__init__('5 for 5', 5)

class TenForTen(RunStreakBadge):
    def __init__(self):
        super(TenForTen, self).__init__('10 for 10', 10)

class TwentyForTwenty(RunStreakBadge):
    def __init__(self):
        super(TwentyForTwenty, self).__init__('20 for 20', 20)

class FiftyForFifty(RunStreakBadge):
    def __init__(self):
        super(FiftyForFifty, self).__init__('50 for 50', 50)

class Perfect100(RunStreakBadge):
    def __init__(self):
        super(Perfect100, self).__init__('Perfect 100', 100)

class ThreeSixtyFiveOf365(RunStreakBadge):
    def __init__(self):
        super(ThreeSixtyFiveOf365, self).__init__('365 of 365', 365)



##################################################################
#
# Badges that require some total distance to be run over the course
# of any number of runs
#
##################################################################
class TotalMileageBadge(CountingUnitsBadge):
    def __init__(self, name, limit, units=UNITS.mile):
        super(TotalMileageBadge, self).__init__(name, limit, units)

    def increment(self, activity):
        return activity['distance'] * UNITS.kilometer

class TenUnderYourBelt(TotalMileageBadge):
    def __init__(self):
        super(TenUnderYourBelt, self).__init__('10 under your belt', 10)

class TwentyUnderYourBelt(TotalMileageBadge):
    def __init__(self):
        super(TwentyUnderYourBelt, self).__init__('20 under your belt', 20)

class FiftyUnderYourBelt(TotalMileageBadge):
    def __init__(self):
        super(FiftyUnderYourBelt, self).__init__('50 under your belt', 50)

class ACenturyDown(TotalMileageBadge):
    def __init__(self):
        super(ACenturyDown, self).__init__('A century down', 100)

class Monster500(TotalMileageBadge):
    def __init__(self):
        super(Monster500, self).__init__('Monster 500', 500)

##################################################################
#
# City to city badges
#
##################################################################
class NYCPhilly(TotalMileageBadge):
    def __init__(self):
        super(NYCPhilly, self).__init__('NYC-Philly', 93)

class LondonParis(TotalMileageBadge):
    def __init__(self):
        super(LondonParis, self).__init__('London-Paris', 232)

class SydneyMelbourne(TotalMileageBadge):
    def __init__(self):
        super(SydneyMelbourne, self).__init__('Sydney-Melbourne', 561)

class NYCChicago(TotalMileageBadge):
    def __init__(self):
        super(NYCChicago, self).__init__('NYC-Chicago', 858)

class MiamiToronto(TotalMileageBadge):
    def __init__(self):
        super(MiamiToronto, self).__init__('Miami-Toronto', 1488)


##################################################################
#
# Badges that require some total distance to be run over a single week
#
##################################################################
class WeeklyTotalMileage(TotalMileageBadge):
    def __init__(self, name, limit, units=UNITS.mile):
        super(WeeklyTotalMileage, self).__init__(name, limit, units)
        self.runs = [] # list of (datetime, distance) tuples

    def increment(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        # FIXME: Is it really 7 days like this or is it calendar days?
        earliest_valid_date = start_date - timedelta(days=7)

        self.runs = [x for x in self.runs if x[0] >= earliest_valid_date]
        self.runs.append((start_date, activity['distance'] * UNITS.kilometer))
        
        # Always reset since we're going to sum ourselves based on runs
        self.reset()
        return sum([x[1] for x in self.runs])

class SolidWeek(WeeklyTotalMileage):
    def __init__(self):
        super(SolidWeek, self).__init__('Solid week', 10)

class RockedTheWeek(WeeklyTotalMileage):
    def __init__(self):
        super(RockedTheWeek, self).__init__('Rocked the week', 25)

##################################################################
#
# Badges that require some total distance to be run in a single month
#
##################################################################
class MonthlyTotalMileageBadge(TotalMileageBadge):
    def __init__(self, name, limit, units=UNITS.mile):
        super(MonthlyTotalMileageBadge, self).__init__(name, limit, units)
        self.datetime_of_lastrun = None

    def increment(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])

        is_new_month = False
        if is_different_month(self.datetime_of_lastrun, start_date):
            is_new_month = True

        if is_new_month:
            self.reset()

        self.datetime_of_lastrun = start_date
        return activity['distance'] * UNITS.kilometer

class SolidMonth(MonthlyTotalMileageBadge):
    def __init__(self):
        super(SolidMonth, self).__init__('Solid month', 30)

class RockedTheMonth(MonthlyTotalMileageBadge):
    def __init__(self):
        super(RockedTheMonth, self).__init__('Rocked the month', 75)

class RunNutMonth(MonthlyTotalMileageBadge):
    def __init__(self):
        super(RunNutMonth, self).__init__('Run nut month', 300)


##################################################################
#
# Badges that require a single run of a specified distance
#
##################################################################
class SingleMileageBadge(CountingUnitsBadge):
    def __init__(self, name, limit, units=UNITS.kilometer):
        super(SingleMileageBadge, self).__init__(name, limit, units)

    def increment(self, activity):
        # Single run, so reset each time
        self.reset()
        return activity['distance'] * UNITS.kilometer

class FiveKer(SingleMileageBadge):
    def __init__(self):
        super(FiveKer, self).__init__('5ker', 5)

class TenKer(SingleMileageBadge):
    def __init__(self):
        super(TenKer, self).__init__('10ker', 10)

class HalfMarathoner(SingleMileageBadge):
    def __init__(self):
        super(HalfMarathoner, self).__init__('Half Marathoner', 13.1, units=UNITS.mile)

class Marathoner(SingleMileageBadge):
    def __init__(self):
        super(Marathoner, self).__init__('Marathoner', 26.2, units=UNITS.mile)

class UltraMarathoner(SingleMileageBadge):
    def __init__(self):
        super(UltraMarathoner, self).__init__('Ultra-Marathoner', 50)

class SingleMileageWithinDuration(CountingUnitsBadge):
    # Note most badges in this subclass are miles, so we change the default
    # units to miles
    def __init__(self, name, limit, duration, units=UNITS.miles):
        super(SingleMileageWithinDuration, self).__init__(name, limit, units)
        self.duration = duration

    def increment(self, activity):
        if (activity['duration'] * UNITS.seconds) < self.duration:
            self.reset()
            return activity['distance'] * UNITS.kilometer
        return 0 * UNITS.kilometer

class BeatA9YearOld(SingleMileageWithinDuration):
    def __init__(self):
        # FIXME: The Smashrun says this is <= 2:55, but then says < 2:55. Not sure which
        super(BeatA9YearOld, self).__init__('Beat a 9yr old', 26.2, (2 * UNITS.hour) + (55 * UNITS.minute))

class PoundedPalin(SingleMileageWithinDuration):
    def __init__(self):
        super(PoundedPalin, self).__init__('Pounded Palin', 26.2, (3 * UNITS.hour) + (59 * UNITS.minute))

class PastDiddy(SingleMileageWithinDuration):
    def __init__(self):
        super(PastDiddy, self).__init__('Past Diddy', 26.2, (4 * UNITS.hour) + (15 * UNITS.minute))

class UnderOprah(SingleMileageWithinDuration):
    def __init__(self):
        super(UnderOprah, self).__init__('Under Oprah', 26.2, (4 * UNITS.hour) + (29 * UNITS.minute))

class ClearedKate(SingleMileageWithinDuration):
    def __init__(self):
        super(ClearedKate, self).__init__('Cleared Kate', 26.2, (5 * UNITS.hour) + (29 * UNITS.minute))

##################################################################
#
# Badges that don't have an associated activity necessarily 
# May also be a badge that requires knowledge outside of what's 
# available via API
#
##################################################################
class NoActivityBadge(Badge):
    def __init__(self, name):
        super(NoActivityBadge, self).__init__(name)

    def add_activity(self, activity):
        pass

    def add_user_info(self, info):
        super(NoActivityBadge, self).add_user_info(info)
        self.actualEarnedDate = srdate_to_datetime(info['dateEarnedUTC'], utc=True)


class Popular(NoActivityBadge):
    def __init__(self):
        super(Popular, self).__init__('Popular')

class OCD(NoActivityBadge):
    def __init__(self):
        super(OCD, self).__init__('OCD')

class GuineaPig(NoActivityBadge):
    def __init__(self):
        super(GuineaPig, self).__init__('Guinea pig')

class BirthdayRun(NoActivityBadge):
    def __init__(self):
        super(BirthdayRun, self).__init__('Birthday Run')

class BroughtABuddy(NoActivityBadge):
    def __init__(self):
        super(BroughtABuddy, self).__init__('Brought a buddy')

class GotFriends(NoActivityBadge):
    def __init__(self):
        super(GotFriends, self).__init__('Got friends')

class SocialSeven(NoActivityBadge):
    def __init__(self):
        super(SocialSeven, self).__init__('Social seven')

class SharesWell(NoActivityBadge):
    def __init__(self):
        super(SharesWell, self).__init__('Shares well')

class PackLeader(NoActivityBadge):
    def __init__(self):
        super(PackLeader, self).__init__('Pack Leader')

class Translator(NoActivityBadge):
    def __init__(self):
        super(Translator, self).__init__('Translator')

class ColorPicker(NoActivityBadge):
    def __init__(self):
        super(ColorPicker, self).__init__('Color Picker')

####################################################
#
# In It For "X" Monthly Badges
#
####################################################
class InItForMonthBadge(CountingUnitsBadge):
    def __init__(self, name, month):
        super(InItForMonthBadge, self).__init__(name, 10, UNITS.day)
        self.month = month
        self.datetime_of_lastrun = None
        self.days = set()

    def reset(self, log=True):
        super(InItForMonthBadge, self).reset(log=log)
        self.days = set()

    def increment(self, activity):
        # FIXME: is using start date correct?
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])

        # This isn't our month. Ignore
        if start_date.month != self.month:
            return 0 * UNITS.month

        # If we've changed years, reset
        if is_different_year(self.datetime_of_lastrun, start_date):
            self.reset()
        self.datetime_of_lastrun = start_date

        if start_date.day not in self.days:
            self.days.add(start_date.day)
            return 1 * UNITS.day
        else:
            # Already have a run on this day. Don't double count
            return 0 * UNITS.day


class InItForJanuary(InItForMonthBadge):
    def __init__(self):
        super(InItForJanuary, self).__init__('In it for January', 1)

class InItForFebruary(InItForMonthBadge):
    def __init__(self):
        super(InItForFebruary, self).__init__('In it for February', 2)

class InItForMarch(InItForMonthBadge):
    def __init__(self):
        super(InItForMarch, self).__init__('In it for March', 3)

class InItForApril(InItForMonthBadge):
    def __init__(self):
        super(InItForApril, self).__init__('In it for April', 4)

class InItForMay(InItForMonthBadge):
    def __init__(self):
        super(InItForMay, self).__init__('In it for May', 5)

class InItForJune(InItForMonthBadge):
    def __init__(self):
        super(InItForJune, self).__init__('In it for June', 6)

class InItForJuly(InItForMonthBadge):
    def __init__(self):
        super(InItForJuly, self).__init__('In it for July', 7)

class InItForAugust(InItForMonthBadge):
    def __init__(self):
        super(InItForAugust, self).__init__('In it for August', 8)

class InItForSeptember(InItForMonthBadge):
    def __init__(self):
        super(InItForSeptember, self).__init__('In it for September', 9)

class InItForOctober(InItForMonthBadge):
    def __init__(self):
        super(InItForOctober, self).__init__('In it for October', 10)

class InItForNovember(InItForMonthBadge):
    def __init__(self):
        super(InItForNovember, self).__init__('In it for November', 11)

class InItForDecember(InItForMonthBadge):
    def __init__(self):
        super(InItForDecember, self).__init__('In it for December', 12)


class AvgPaceBadge(CountingBadge):
    def __init__(self, name, pace, limit=10, slower_ok=False):
        super(AvgPaceBadge, self).__init__(name, limit)
        self.pace = pace
        self.datetime_of_lastrun = None
        if slower_ok:
            self.meets_criteria = lambda x, y: x >= y
        else:
            self.meets_criteria = lambda x, y: x <= y

    def increment(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])

        # Reset if we've changed months since the last activity
        if is_different_month(self.datetime_of_lastrun, start_date):
            self.reset()
        self.datetime_of_lastrun = start_date

        if self.meets_criteria(avg_pace(activity), self.pace):
            return 1
        return 0

class EasyRunner(AvgPaceBadge):
    def __init__(self):
        super(EasyRunner, self).__init__('Easy runner', 10, slower_ok=True)

class ChillRunner(AvgPaceBadge):
    def __init__(self):
        super(ChillRunner, self).__init__('Chill runner', 12, slower_ok=True)

class RoadRunner(AvgPaceBadge):
    def __init__(self):
        super(RoadRunner, self).__init__('Roadrunner', 8, slower_ok=False)

class Mercury(AvgPaceBadge):
    def __init__(self):
        super(Mercury, self).__init__('Mercury', 7, slower_ok=False)

class FastAndSlow(Badge):
    def __init__(self):
        super(FastAndSlow, self).__init__('Fast & Slow')
        self.fast = 0
        self.slow = 0

    def add_activity(self, activity):
        if avg_pace(activity) < 8:
            self.fast += 1
        if avg_pace(activity) > 10:
            self.slow += 1
        if self.fast >= 10 and self.slow >= 10:
            self.acquire(activity)

####################################################
#
# Stairs
#
####################################################
class StairsBadge(Badge):
    def __init__(self, name, min_months, delta):
        super(StairsBadge, self).__init__(name)
        self.delta = delta
        self.stepped = False
        self.step_activity = None
        self.min_months = min_months
        self.cur_month = 0 * UNITS.miles
        self.prev_month = 0 * UNITS.miles
        self.consecutive_months = 0
        self.prev_activity_datetime = None

    def update_cur_month_value(self, distance):
        self.cur_month += distance

    def add_activity(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        distance = activity['distance'] * UNITS.kilometer

        # If we walked into a new month, figure out if last month contained a step
        if is_different_month(self.prev_activity_datetime, start_date):
            if self.stepped:
                self.consecutive_months += 1
                result = 'STEP #%d' % (self.consecutive_months)
            else:
                # Sad trombone!
                result = 'FAIL'
                self.consecutive_months = 0

            if self.prev_activity_datetime is not None:
                logging.debug("%s: Distance for %s/%s: %s [%s]" % (self.name, self.prev_activity_datetime.month, self.prev_activity_datetime.year, self.cur_month, result))
            self.stepped = False
            self.prev_month = self.cur_month
            self.cur_month = 0 * UNITS.miles

        # Smashrun seems to round this way, so do it here too
        self.update_cur_month_value(round(distance.to(UNITS.miles).magnitude, 2) * UNITS.miles)
        self.prev_activity_datetime = start_date

        if not self.stepped:
            if self.prev_month > (0 * UNITS.miles):
                if self.delta is None:
                    if self.cur_month > self.prev_month:
                        self.stepped = True
                        self.step_activity = activity
                elif self.cur_month > (self.prev_month + self.delta):
                    self.stepped = True
                    self.step_activity = activity

        if not self.acquired:
            if self.consecutive_months >= self.min_months:
                self.acquire(self.step_activity)



class Stairs(StairsBadge):
    def __init__(self):
        super(Stairs, self).__init__('Stairs', 4, None)

class SteepStairs(StairsBadge):
    def __init__(self):
        super(SteepStairs, self).__init__('Steep stairs', 4, 5 * UNITS.miles)

class LongStairs(StairsBadge):
    def __init__(self):
        super(LongStairs, self).__init__('Long stairs', 6, None)

class LongSteepStairs(StairsBadge):
    def __init__(self):
        super(LongSteepStairs, self).__init__('Long/Steep stairs', 6, 5 * UNITS.miles)

class ToweringStairs(StairsBadge):
    def __init__(self):
        super(ToweringStairs, self).__init__('Towering stairs', 6, 10 * UNITS.miles)

####################################################
#
# Further
#
####################################################
class FurtherBadge(StairsBadge):
    def __init__(self, name, min_months, delta):
        super(FurtherBadge, self).__init__(name, min_months, delta)

    def update_cur_month_value(self, distance):
        self.cur_month = max(self.cur_month, distance)

class FourFurther(FurtherBadge):
    def __init__(self):
        super(FourFurther, self).__init__('Four further', 4, None)

class FourFarFurther(FurtherBadge):
    def __init__(self):
        super(FourFarFurther, self).__init__('Four far further', 4, 2 * UNITS.kilometer)

class SixFurther(FurtherBadge):
    def __init__(self):
        super(SixFurther, self).__init__('Six further', 6, None)

class SixFarFurther(FurtherBadge):
    def __init__(self):
        super(SixFarFurther, self).__init__('Six far further', 6, 2 * UNITS.kilometer)

class FurtherToFarther(FurtherBadge):
    def __init__(self):
        super(FurtherToFarther, self).__init__('Further to farther', 6, 5 * UNITS.kilometer)

####################################################
#
# Elevation in a single run
#
####################################################
class SingleElevationBadge(Badge):
    def __init__(self, name, height):
        super(SingleElevationBadge, self).__init__(name)
        self.height = height

    def add_activity(self, activity):
        delta = sr_elevation_delta(activity)
        if delta >= self.height:
            self.acquire(activity)

class ToweredPisa(SingleElevationBadge):
    def __init__(self):
        super(ToweredPisa, self).__init__('Towered Pisa', 56 * UNITS.meters)

class TopOfWashington(SingleElevationBadge):
    def __init__(self):
        super(TopOfWashington, self).__init__('Top of Washington', 169 * UNITS.meters)

class OverTheEiffel(SingleElevationBadge):
    def __init__(self):
        super(OverTheEiffel, self).__init__('Over the Eiffel', 301 * UNITS.meters)

class AboveTheBurj(SingleElevationBadge):
    def __init__(self):
        super(AboveTheBurj, self).__init__('Above the Burj', 830 * UNITS.meters)

class ToPikesPeak(SingleElevationBadge):
    def __init__(self):
        super(ToPikesPeak, self).__init__('To Pike\'s Peak', 2382 * UNITS.meters)


####################################################
#
# Elevation in a single month
#
####################################################
class MonthlyElevationBadge(CountingUnitsBadge):
    def __init__(self, name, limit, units=UNITS.meters):
        super(MonthlyElevationBadge, self).__init__(name, limit, units)
        self.datetime_of_lastrun = None

    def increment(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        if is_different_month(self.datetime_of_lastrun, start_date):
            self.reset()

        return sr_elevation_delta(activity)

class TopOfTable(MonthlyElevationBadge):
    def __init__(self):
        super(TopOfTable, self).__init__('Top of Table', 1085)

class ClimbedHalfDome(MonthlyElevationBadge):
    def __init__(self):
        super(ClimbedHalfDome, self).__init__('Climbed Half Dome', 2694)

class ReachedFitzRoy(MonthlyElevationBadge):
    def __init__(self):
        super(ReachedFitzRoy, self).__init__('Reached Fitz Roy', 3359)

class MatterhornMaster(MonthlyElevationBadge):
    def __init__(self):
        super(MatterhornMaster, self).__init__('Matterhorn master', 4478)

class ConqueredEverest(MonthlyElevationBadge):
    def __init__(self):
        super(ConqueredEverest, self).__init__('Conquered Everest', 8848)

####################################################
#
# Pace variability badges
#
####################################################
class PaceVariabilityBadge(CountingBadge):
    def __init__(self, name, distance, limit, tolerance):
        super(PaceVariabilityBadge, self).__init__(name, limit)
        self.tolerance = tolerance

    def increment(self, activity):
        variability = sr_pace_variability(activity)
        if variability <= self.tolerance:
            return 1
        return 0

class ShortAndSteady(PaceVariabilityBadge):
    def __init__(self):
        super(ShortAndSteady, self).__init__('Short and steady', 5 * UNITS.kilometer, 10, .05)

class LongAndSteady(PaceVariabilityBadge):
    def __init__(self):
        super(LongAndSteady, self).__init__('Long and steady', 10 * UNITS.kilometer, 10, .05)

class ShortAndSolid(PaceVariabilityBadge):
    def __init__(self):
        super(ShortAndSolid, self).__init__('Short and solid', 5 * UNITS.kilometer, 10, .04)

class LongAndSolid(PaceVariabilityBadge):
    def __init__(self):
        super(LongAndSolid, self).__init__('Long and solid', 10 * UNITS.kilometer, 10, .04)

class LongAndRockSolid(PaceVariabilityBadge):
    def __init__(self):
        super(LongAndRockSolid, self).__init__('Long and rock solid', 10 * UNITS.kilometer, 10, .03)

####################################################
#
# Limited Badges
#
####################################################
class Corleone(Badge):
    def __init__(self):
        super(Corleone, self).__init__('Corleone')
        self.datetime_of_lastrun = None

    def add_activity(self, activity):
        start_date = srdate_to_datetime(activity['startDateTimeLocal'])
        if self.datetime_of_lastrun is not None:
            if (start_date - self.datetime_of_lastrun).days >= 30:
                self.acquire(activity)

        self.datetime_of_lastrun = start_date

class Veteran(NoActivityBadge):
    # http://smashrun.com/steve.tant/badges-to-go/4
    def __init__(self):
        super(Veteran, self).__init__('Veteran')

class SmashrunForLife(NoActivityBadge):
    # http://smashrun.com/steve.tant/badges-to-go/4
    def __init__(self):
        super(SmashrunForLife, self).__init__('Smashrun for life')

