#!/usr/bin/env python3

#
# Funny.py: It's funny because I have no idea what this code does :)
#
# Disclaimer: By the GPL, I take no responsibility for what this code does. 
# This code is technically free speech: I don't know what this code is for and
# why it's here.
# 

from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from dateutil import tz
import time
import re
import logging
import sqlite3

# Source of the funny
FUNNY_SRC = "https://nitter.net/WesternWeightRm"  # Sorry, kind folks at nitter
# NOTE: Change the subroutines in obtain_the_funny() upon change of FUNNY_SRC!

# location of database file
DB_PATH = "stats.db"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='funny.log',  # Specify the log file name
    filemode='a'  # Append to the log file (use 'w' to overwrite)
)
logger = logging.getLogger("funny routine")


def init_db():
    """Ensures database has been initialized, and returns a database connection"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS stats (
                       timestamp INTEGER NOT NULL UNIQUE,
                       wr INTEGER,
                       cm INTEGER,
                       spin INTEGER,
                       id INT NOT NULL UNIQUE,
                       PRIMARY KEY (id)
                   );""");
    # Create an index on timestamp: fast query on time
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_timestamp ON stats(timestamp);")
    conn.commit()
    cur.close()
    return conn


def insert_funny(db_conn, funnies):
    """Insert a list of funnies (as tuples) into the database and commit"""
    cur = db_conn.cursor()
    cur.executemany("INSERT OR REPLACE INTO stats VALUES (?, ?, ?, ?, ?)",
                     funnies)
    db_conn.commit()
    cur.close()


def obtain_the_funny(db_conn, how_many_funnies: int = 1, headless: bool = True):
    """Returns a list of all the funnies (as tuples) from FUNNY_SRC"""

    _funny_options = webdriver.firefox.options.Options()
    if headless:
        _funny_options.add_argument("--headless")
    funny_machine = webdriver.Firefox(options=_funny_options)
    funny_machine.get(FUNNY_SRC)

    # Result: a list of all the funny
    res = []

    # SUBROUTINES HERE -- will need to be changed after every change of FUNNY_SRC
    def find_more_funnies():
        """Routine to find the next funny"""
        load_more_maybe = [ x.find_element(By.TAG_NAME, "a") for x in funny_machine.find_elements(By.CLASS_NAME, "show-more") ]
        for e in load_more_maybe:
            if e.get_attribute("innerHTML") == "Load more":
                e.click()
                break

    def obtain_subfunnies():
        """Routine to separate all the funnies"""
        funnies = (funny_machine.find_element(By.CLASS_NAME, "timeline")
                                .find_elements(By.CLASS_NAME, "timeline-item"))
        # Regex to remove all characters I don't care about
        not_alnum_filter = re.compile("[^a-z0-9\n]+")
        # Regex to ensure the funny is there
        funny_filter = re.compile("(wr|cm|spin)[0-9]+")
        for f in funnies:
            entry = { "timestamp": None, "wr": None, "cm": None, "spin": None, "id": None } 
            # timestamp, wr, cm, spin, id = None, None, None, None, None
            if len(f.find_elements(By.CLASS_NAME, "tweet-body")) != 0:
                # Extracting the funny from the subfunny
                wr_cm_spin_maybe = (f.find_element(By.CLASS_NAME, "tweet-content")
                                     .get_attribute("innerHTML"))
                # Sanitize the funny string
                wr_cm_spin_maybe = (not_alnum_filter.sub('', wr_cm_spin_maybe.lower())
                                                    .strip()
                                                    .split('\n'))
                # Find all funnies
                wr_cm_spin_maybe = [ re.match(funny_filter, s) for s in wr_cm_spin_maybe ]
                wr_cm_spin_maybe = [ s[0] for s in filter(lambda x: x != None, wr_cm_spin_maybe) ]
                # Ignore subfunny if there is no actual funny
                if not len(wr_cm_spin_maybe):
                    continue

                # At this point we can conclude this is funny. Find the ID first,
                # and then populate the rest of the data. This is also done for
                # logging purposes, so logs can contain id's

                # Populating ID and timestamp:
                # HTML element from the website with both time and id
                time_id_elem = (f.find_element(By.CLASS_NAME, "tweet-name-row")
                                 .find_element(By.CLASS_NAME, "tweet-date")
                                 .find_element(By.TAG_NAME, "a"))
                entry["id"] = int(time_id_elem.get_attribute("href")[len("https://nitter.net/WesternWeightRm/status/"):-len("#m")])
                time_str = time_id_elem.get_attribute("title")
                print(time_str)
                entry["timestamp"] = int(datetime.strptime(time_str, "%b %d, %Y · %I:%M %p UTC")
                                                 .replace(tzinfo=tz.gettz("UTC"))
                                                 .timestamp())

                # Actually populating wr, cm, spin:
                for stat in wr_cm_spin_maybe:
                    for stat_type in ["wr", "cm", "spin"]:
                        if stat_type in stat:
                            if entry[stat_type]:
                                logger.warn(f"Encountered duplicate {stat_type} entry in post id {entry['id']}!")
                            entry[stat_type] = int(stat[len(stat_type):])

                    # # you think you're and can put this in a for loop but this might actually be more efficient honestly, due to compiler optimizations:
                    # if "wr" in stat:
                    #     if wr != None: logger.warn(f"Encountered duplicate WR entry in post id {id}!")
                    #     entry["wr"] = int(stat[2:])
                    # elif "cm" in stat:
                    #     if cm != None: logger.warn(f"Encountered duplicate CM entry in post id {id}!")
                    #     entry["cm"] = int(stat[2:])
                    # elif "spin" in stat:
                    #     if spin != None: logger.warn(f"Encountered duplicate SPIN entry in post id {id}!")
                    #     entry["spin"] = int(stat[4:])
                if entry["wr"] == None and entry["cm"] == None and entry["spin"] == None:
                    logger.warning(f"post id {entry['id']} has no entries!")
                    continue
                print(entry)
                res.append(tuple(entry.values()))

    # Each funny is 20 smaller funnies. If there is about 40 funnies in a day,
    # then I need 2 funnies to capture roughly a single day, hence the 2 here.
    for _ in range(how_many_funnies * 2):
        time.sleep(4) # Out of courtesy: I am not going to spam a FOSS service to death.
        obtain_subfunnies()
        find_more_funnies()
    funny_machine.quit()
    return res

# MAIN LOGIC
db_conn = init_db()
db_cur = db_conn.cursor()
# 2 weeks worth of funny
insert_funny(db_conn, obtain_the_funny(db_conn, headless=True, how_many_funnies=1))
db_conn.close()
