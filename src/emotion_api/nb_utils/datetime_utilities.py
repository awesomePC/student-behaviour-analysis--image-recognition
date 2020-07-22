"""This module provides datetime utilities."""
import time
from datetime import datetime as dt
from datetime import timedelta, timezone, date

from dateutil import parser

import logging
logger = logging.getLogger(__name__)
# print(__name__)

def modify_date_time(
    date,
    add_days=False,
    add_minutes=False,
    substract_days=False,
    return_type='datetime',
    strftime_format='%Y-%m-%dT%H:%M:%SZ'
    ):
    """
    * modify date as per passed parameters
    --------------------------------------
    @ parameters--
        * date -- Input date
        * add_days -- Number of days to add. Default False.
        * add_minutes -- Number of minutes to add. Default False.
        * substract_days -- Number of days to substract. Default False.
        * return_type -- return type of processed data either timestamp, string etc.
        * strftime_format -- Used if return type is stings
    -------------------------------------------------------
    @ output:
        * Either timestamp or string
    """
    original_date = date
    
    if add_days:
       date = date + timedelta(days=add_days)
    
    if add_minutes:
       date = date + timedelta(minutes=add_minutes)
    
    if substract_days:
       date = date - timedelta(days=substract_days)

    if return_type in 'datetime':
        return date
    
    elif return_type in 'timestamp':
        date_timestamp = date.replace(
            tzinfo=timezone.utc
        ).timestamp()
        return date_timestamp
    else:
        date_str = dt.strftime(
            date, strftime_format
        )
        return date_str
        
def get_today_datetime():
    """
    * Get today UTC, local, Rounded down datetime 
    * ex.
     utc_datetime     =  2017-01-09 11:02:39.925243
     local_datetime   =  2017-01-09 16:32:39.925243
     rounded_down_datetime = 2017-01-09 00:00:00
    """
    utc_datetime = dt.utcnow()
    local_datetime = dt.now()
    rounded_down_datetime = utc_datetime.replace(
        microsecond=0, second=0, minute=0, hour=0
    )
    return (
        utc_datetime,
        local_datetime,
        rounded_down_datetime
    )

def generate_date_range(
    datetime_since, datetime_until, include_datetime_until=False
):
    """
    Generate date range from start date and end date
    by default it excludes end date from list
    
    Arguments:
        datetime_since {datetime} -- (start_date) lower bound of date
        datetime_until {datetime} -- (end_date) upper bound of date
    
    Keyword Arguments:
        include_datetime_until {bool} -- include end date (default: {False})
    """
    delta = datetime_until - datetime_since

    # list comprehension - this will give you a list 
    # containing all of the dates
    list_datetimes = [
        datetime_since + timedelta(days=x) for x in range(delta.days)
    ]

    if include_datetime_until:
        list_datetimes.append(datetime_until)

    return list_datetimes

def convert_date_2_str(date, date_str_format="%Y-%m-%dT%H:%M:%S"):
    """
    Convert date type to string representation
    
    Arguments:
        date {datetime} -- Datetime object
    
    Keyword Arguments:
        date_str_format {str} - string date format (default: {"%Y-%m-%dT%H:%M:%S"})
    
    Returns:
        str -- string representation of date
    """
    if isinstance(date, str):
        date = parser.parse(
            date
        )
        str_date = date.strftime(
            date_str_format
        )
    else:
        # if already date
        str_date = date.strftime(
            date_str_format
        )
    return str_date