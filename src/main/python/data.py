#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum, auto
from dataclasses import dataclass

import numpy as np
import pandas as pd


class StrEnum(str, Enum):
    pass


# this creates nice lowercase and JSON serializable names
# https://docs.python.org/3/library/enum.html#using-automatic-values
class AutoNameLower(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class AutoNameLowerStrEnum(AutoNameLower):
    pass


class ParkingPosition(AutoNameLowerStrEnum):
    PRIVATE = auto()
    PUBLIC = auto()
    DIFFERENT = auto()
    NA = auto()


class HouseholdType(AutoNameLowerStrEnum):
    MULTI_W_CHILDREN = auto()
    MULTI_WO_CHILDREN = auto()
    SINGLE = auto()


class EconomicStatus(AutoNameLowerStrEnum):
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()
    UNKNOWN = auto()


class Gender(AutoNameLowerStrEnum):
    M = auto()
    F = auto()
    OTHER = auto()


class Employment(AutoNameLowerStrEnum):
    CHILD = auto()
    HOMEMAKER = auto()
    RETIREE = auto()
    UNEMPLOYED = auto()
    SCHOOL = auto()
    STUDENT = auto()
    TRAINEE = auto()

    JOB_FULL_TIME = auto()
    JOB_PART_TIME = auto()
    OTHER = auto()


class Availability(AutoNameLowerStrEnum):
    YES = auto()
    NO = auto()
    UNKNOWN = auto()


class Purpose(AutoNameLowerStrEnum):
    WORK = auto()
    WORK_BUSINESS = auto()
    EDU_PRIMARY = auto()  # Edu could be split further
    EDU_HIGHER = auto()
    EDU_OTHER = auto()
    SHOP_FOOD = auto()
    SHOP_OTHER = auto()
    PERSONAL_BUSINESS = auto()
    TRANSPORT = auto()
    LEISURE = auto()
    DINING = auto()
    OUTSIDE_RECREATION = auto()
    VISIT = auto()  # Check if needed
    HOME = auto()
    OTHER = auto()


class TripMode(AutoNameLowerStrEnum):
    WALK = auto()
    BIKE = auto()
    CAR = auto()
    RIDE = auto()
    PT = auto()
    OTHER = auto()


class DistanceGroup(AutoNameLowerStrEnum):
    """ These distance groups are designed so that they are roughly equally populated. """

    ZERO = auto()
    G_500M = auto()
    G_1KM = auto()
    G_2KM = auto()
    G_3KM = auto()
    G_5KM = auto()
    G_10KM = auto()
    G_25KM = auto()
    G_50KM = auto()
    G_100KM = auto()
    OVER_100KM = auto()

    @staticmethod
    def cut(values):
        bins = [0, 0.5, 1, 2, 3, 5, 10, 25, 50, 100]
        values = np.asarray(values)

        idx = np.digitize(values, bins, right=True)
        # Set ZERO group manually
        idx[np.where(values <= 0)] = 0
        return np.take(np.asarray(DistanceGroup, dtype=object), idx, axis=0)


class DurationGroup(AutoNameLowerStrEnum):
    """ Most common duration groups, right side is inclusive e.g <= 5 min """

    G_5MIN = auto()
    G_15MIN = auto()
    G_30MIN = auto()
    G_60MIN = auto()
    G_120MIN = auto()
    G_180MIN = auto()
    G_300MIN = auto()
    G_420MIN = auto()
    G_480MIN = auto()
    G_510MIN = auto()
    G_570MIN = auto()
    G_660MIN = auto()
    G_750MIN = auto()
    REST_OF_DAY = auto()

    @staticmethod
    def cut(values):
        bins = [5, 15, 30, 60, 120, 180, 300, 420, 480, 510, 570, 660, 750]

        values = np.asarray(values)
        idx = np.digitize(values, bins, right=True)
        return np.take(np.asarray(DurationGroup, dtype=object), idx, axis=0)


class SourceDestinationGroup(AutoNameLowerStrEnum):
    HOME_WORK = auto()
    HOME_CHILDCARE = auto()
    HOME_EDU = auto()
    HOME_BUSINESS = auto()
    HOME_SHOP = auto()
    HOME_LEISURE = auto()
    HOME_OTHER = auto()
    WORK_HOME = auto()
    CHILDCARE_HOME = auto()
    EDU_HOME = auto()
    BUSINESS_HOME = auto()
    SHOP_HOME = auto()
    LEISURE_HOME = auto()
    OTHER_HOME = auto()
    OTHER_WORK = auto()
    WORK_OTHER = auto()
    OTHER_OTHER = auto()

    UNKNOWN = auto()

    def source(self):
        if self.name.startswith("HOME"):
            return Purpose.HOME
        elif self.name.startswith("WORK"):
            return Purpose.WORK

        return Purpose.OTHER


@dataclass
class Household:
    """ Universal definition of household attributes """
    hh_id: str
    h_weight: float
    n_persons: int
    n_cars: int
    n_bikes: int
    n_other_vehicles: int
    car_parking: ParkingPosition
    economic_status: EconomicStatus
    type: HouseholdType
    location: str
    regionType: int


@dataclass
class Person:
    """ Universal definition of person attributes."""
    p_id: str
    p_weight: float
    hh: str
    age: int
    gender: Gender
    restricted_mobility: bool
    employment: Employment
    driving_license: Availability
    car_avail: Availability
    bike_avail: Availability
    pt_abo_avail: Availability
    mobile_on_day: bool
    present_on_day: bool


@dataclass
class Trip:
    """ Universal definition of trip attributes"""
    t_id: str
    t_weight: float
    p_id: str
    n: int
    day_of_week: int
    departure: int
    duration: int
    gis_length: float
    main_mode: TripMode
    purpose: Purpose
    sd_group: SourceDestinationGroup
    valid: bool


@dataclass
class Activity:
    """ Activity information (including leg) """
    a_id: str
    p_id: str
    n: int
    type: Purpose
    duration: int
    leg_dist: int
    leg_mode: TripMode


def read_srv(household_file, person_file, trip_file):
    """ Read SrV into pandas format """

    hh = pd.read_csv(household_file, encoding="windows-1252", delimiter=";", decimal=",",
                     quotechar="\"", low_memory=False, quoting=2)

    p = pd.read_csv(person_file, encoding="windows-1252", delimiter=";", decimal=",",
                    quotechar="\"", low_memory=False, quoting=2)

    t = pd.read_csv(trip_file, encoding="windows-1252", delimiter=";", decimal=",",
                    quotechar="\"", low_memory=False, quoting=2)

    return hh, p, t


def pint(x):
    """ Convert to positive integer"""
    return max(0, int(x))


def srv_to_standard(data: tuple):
    """ Convert srv data to standardized survey format """

    # Needs to be importer late
    from converter import SrV2018

    (hh, pp, tt) = data

    ps = []
    for p in pp.itertuples():
        ps.append(
            Person(
                str(int(p.HHNR)) + "_" + str(int(p.PNR)),
                p.GEWICHT_P,
                str(int(p.HHNR)),
                int(p.V_ALTER),
                SrV2018.gender(p.V_GESCHLECHT),
                False if p.V_EINSCHR_NEIN else True,
                SrV2018.employment(p.V_ERW),
                SrV2018.yes_no(p.V_FUEHR_PKW),
                SrV2018.veh_avail(p.V_PKW_VERFUEG),
                Availability.YES if SrV2018.veh_avail(p.V_RAD_VERFUEG) == Availability.YES or SrV2018.veh_avail(
                    p.V_ERAD_VERFUEG) == Availability.YES else SrV2018.veh_avail(p.V_RAD_VERFUEG),
                SrV2018.veh_avail(p.V_FK_VERFUEG),
                p.V_WOHNUNG == 1,
                p.V_WOHNORT == 1
            )
        )

    ps = pd.DataFrame(ps).set_index("p_id")

    hhs = []
    for h in hh.itertuples():
        hh_id = str(int(h.HHNR))
        hhs.append(
            Household(
                hh_id,
                h.GEWICHT_HH,
                pint(h.V_ANZ_PERS),
                pint(h.V_ANZ_PKW_PRIV + h.V_ANZ_PKW_DIENST),
                pint(h.V_ANZ_RAD + h.V_ANZ_ERAD),
                pint(h.V_ANZ_MOT125 + h.V_ANZ_MOPMOT + h.V_ANZ_SONST),
                SrV2018.parking_position(h.V_STELLPL1),
                SrV2018.economic_status(h.V_EINK, ps[ps.hh == hh_id]),
                SrV2018.household_type(h.E_HHTYP),
                h.ST_CODE_NAME,
                0  # TODO
            )
        )

    ts = []
    for t in tt.itertuples():
        # TODO: E_DAUER, E_GESCHW
        # E_ANKUNFT
        # TODO: strange
        ts.append(
            Trip(
                str(int(t.HHNR)) + "_" + str(int(t.PNR)) + "_" + str(int(t.WNR)),
                t.GEWICHT_W,
                str(int(t.HHNR)) + "_" + str(int(t.PNR)),
                int(t.WNR),
                int(t.STICHTAG_WTAG),
                int(t.E_BEGINN),
                int(t.E_DAUER),
                float(t.GIS_LAENGE),
                SrV2018.trip_mode(t.E_HVM),
                SrV2018.trip_purpose(t.V_ZWECK),
                SrV2018.sd_group(int(t.E_QZG_17)),
                t.E_WEG_GUELTIG != 0
            )
        )

    return pd.DataFrame(hhs).set_index("hh_id"), ps, pd.DataFrame(ts).set_index("t_id")


if __name__ == "__main__":
    import argparse

    d = "/Users/rakow/Development/matsim-scenarios/shared-svn/projects/matsim-berlin/data/SrV/Brandenburg/"

    srv = read_srv(d + "H2018.csv", d + "P2018.csv", d + "W2018.csv")

    (hh, pp, tt) = srv_to_standard(srv)