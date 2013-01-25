#!/usr/bin/env python
import re
import datetime
import operator
import sys
import os


class Player():
    name = None
    play_time = 0
    last_seen = None


def build_pretty_time_string(total):
    time = "%20s | " % player
    days = total / 86400
    if days > 0:
        time += "%2s days" % int(days)
        total -= int(days) * 86400
    else:
        time += "       "
    hours = total / 3600
    if hours > 0:
        time += " %2s hours" % int(hours)
        total -= int(hours) * 3600
    else:
        time += "         "
    mins = total / 60
    if mins > 0:
        time += " %2s minutes" % int(mins)
        total -= int(mins) * 60
    else:
        time += "           "
    if total > 0:
        time += " %2s seconds" % total
    return time

actions = {
    "login": re.compile("([0-9]{4})\-([0-9]{2})\-([0-9]{2}) ([0-2][0-9])\:([0-9]{2})\:([0-9]{2}) \[INFO\] ([A-z0-9]*) ?\[\/[0-9.]{4,15}\:[0-9]*\]"),
    "logout": re.compile("([0-9]{4})\-([0-9]{2})\-([0-9]{2}) ([0-2][0-9])\:([0-9]{2})\:([0-9]{2}) \[INFO\] ([A-z0-9]*) lost connection")
}

server_log = 'server.log'

try:
    server_log = sys.argv[1]
except IndexError: # no argument supplied in the command prompt, then see if we find server.log in the current dir
    if os.path.exists(os.path.join(os.getcwd(), 'server.log')):
        server_log = os.path.join(os.getcwd(), 'server.log')

if os.path.exists(server_log):
    with open(server_log, 'r') as f: #open file then close it
        file_contents = f.readlines()
else:
    print 'Could not locate "server.log" - try adding the full path to the log file as an argument, or simply running ' \
          'this script in the same directory as the server.log file'
    sys.exit(1)

online = {}
totals = {}

for line in file_contents:
    regex = None
    action = None
    player = None
    time = None
    for action in actions:
        if actions[action].match(line):
            regex = actions[action]
            break

    if regex:
        # Get the user's name and parse the datetime
        data = regex.split(line)
        player = data[7]
        time = datetime.datetime(int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]), int(data[6]))

        # Now do things!
        if action is "login":
            online[player] = time

            if player not in totals:
                totals[player] = Player()

        elif action is "logout":
            delta = time - online[player]
            totals[player].play_time += delta.seconds

            # Get the last logged in date/time
            if totals[player].last_seen:
                if time > totals[player].last_seen:
                    totals[player].last_seen = time
            else:
                totals[player].last_seen = time

results = []

for player in totals:
    pretty_time_string = build_pretty_time_string(totals[player].play_time)
    results.append([pretty_time_string, totals[player].last_seen, totals[player].name, totals[player].play_time])

s_results = sorted(results, key=operator.itemgetter(3))
s_results.reverse()

for res in s_results:
    print "{0}) {1} | Last Seen On: {2}".format(s_results.index(res) + 1, res[0], res[1])
f.close()