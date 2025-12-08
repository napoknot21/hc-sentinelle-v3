from __future__ import annotations

import datetime as dt

from typing import Optional

from src.utils.formatters import str_to_date


def previous_business_day (date : Optional[str | dt.datetime | dt.date] = None) -> dt.date:
    """
    Adjust the date back to the previous business day
    if it falls on Saturday or Sunday.
    Does NOT handle public holidays.
    """
    date = str_to_date(date) 

    while date.weekday() >= 5 :  # 5 = saturday, 6 = sunday
        date -= dt.timedelta(days=1)

    return date


def monday_of_week(date : Optional[str | dt.datetime | dt.date] = None) -> dt.date :
    """
    Return the Monday of the week containing date d.
    Monday = weekday 0.
    """
    date = str_to_date(date) 
    monday = date - dt.timedelta(days=date.weekday())

    return monday


def get_qtd_from_date (date_ref : Optional[str | dt.datetime | dt.date] = None) -> dt.date :
    """
    Compute the QTD start:
    → take the day *before* the first day of the current quarter,
    → adjust to previous business day if it falls on a weekend.
    """
    quarter = (date_ref.month - 1) // 3 + 1              # Quarter number: 1..4
    first_month_of_quarter = 3 * (quarter - 1) + 1      # 1, 4, 7, 10

    first_day_of_quarter = dt.date(date_ref.year, first_month_of_quarter, 1)
    start = first_day_of_quarter - dt.timedelta(days=1)

    return start


def get_mtd_start (date_ref : Optional[str | dt.datetime | dt.date] = None) -> dt.date :
    """
    Compute the MTD start:
    → take the day *before* the first day of the month,
    → adjust to previous business day if it falls on a weekend.
    """
    first_day_of_month = date_ref.replace(day=1)
    start = first_day_of_month - dt.timedelta(days=1)

    return start
