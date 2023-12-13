#!/usr/bin/env python3

import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
from dateutil import tz

# location of database file
DB_PATH = "stats.db"


# def datetime_to_date(day, timezone=None):
#     return datetime(year=day.year, month=day.month, date=day.date, hour=0,
#                      minute=0, second=0, microsecond=0, tzinfo=timezone)
# 
# 
# def get_day_range(local_day):
#     """Obtain a tuple containing the beginning and end of the current day in unix timestamp (in UTC)"""
#     # I assume the computer is in the same timezone as the gym....
#     start = datetime_to_date(local_day, tz.tzlocal())
#     end = start + timedelta(days=1)
#     return (int(start.timestamp()), int(end.timestamp()))


def fetch_day_stats(conn, day_range):
    """Gather the stats for a sinle day, given a timestamp in that day"""
    cur = conn.cursor()
    print(f"{int(day_range[0].timestamp())} AND {int(day_range[1].timestamp())}")
    day_stats = cur.execute(f"SELECT * FROM stats WHERE timestamp BETWEEN {int(day_range[0].timestamp())} AND {int(day_range[1].timestamp())};")
    res = day_stats.fetchall()
    print(res)
    cur.close()
    return res


def graph(x_axis, y_axis, x_lim):
    plt.figure()
    plt.xlim(x_lim)
    plt.scatter(x_axis, y_axis)
    plt.xticks([], [])

    # TODO draw the regression line
    plt.show()

db_conn = sqlite3.connect(DB_PATH)
# 5:00 -- 23:59
x_lim = ((datetime.today() - timedelta(days=3)).replace(hour=5, minute=0, second=0, microsecond=0),#, tzinfo=tz.tzlocal()),
         (datetime.today() - timedelta(days=3)).replace(hour=23, minute=59, second=0, microsecond=0))#, tzinfo=tz.tzlocal()))
day_stats = fetch_day_stats(db_conn, x_lim)
print([ x.timestamp() for x in x_lim ])
graph([ x[0] for x in day_stats ], [ x[1] for x in day_stats ], [ x.timestamp() for x in x_lim ])
