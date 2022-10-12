import json
import requests

f = open("config.json", "r")

cfg = json.load(f)

endpoints = cfg["endpoints"]

schedules = {}
names = []

for name in endpoints:
    names.append(name)
    e = endpoints[name]
    schedules[name] = requests.get(e).json()

class Match:
    def __init__(self, time, day, p1, p2, priority):
        self.time = time
        self.day = day
        self.p1 = p1
        self.p2 = p2
        self.priority = priority
    def contains_users(self, p1, p2):
        return (self.p1 == p1 and self.p2 == p2) or (self.p2 == p1 and self.p1 == p2)

class Day:
    def __init__(self, name):
        self.name = name
        self.times = {}
        for i in range(24):
            self.times[f"{i}:00"] = []
    def get_matches(self):
        out = []
        for t in self.times:
            people = self.times[t]
            if len(people) > 1:
                matched = []
                for p_1 in people:
                    for p_2 in people:
                        if p_1 != p_2 and (p_2, p_1) not in matched:
                            matched.append((p_1, p_2))
                            out.append(Match(t, self.name, p_1["name"], p_2["name"], p_1["priority"] + p_2["priority"]))
        return out

d_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
days = {}

for d in d_list:
    days[d] = Day(d)

for name in schedules:
    schedule = schedules[name]
    for hour in schedule:
        for day in d_list:
            if day in hour and hour[day].isnumeric():
                priority = int(hour[day])
                max(min(priority, 5), 1)
                days[day].times[hour["UTC"]].append({"name": name, "priority": priority})
matches = []
for day in days:
    d = days[day]
    matches += d.get_matches()

matches.sort(key=lambda x: x.priority, reverse=True)

for match in matches:
    print(f"Match between {match.p1} and {match.p2} at {match.time} on {match.day} with a priority of {match.priority}")


games = []
for p_1 in names:
    for p_2 in names:
        if p_1 == p_2:
            continue
        contains_user = False
        for game in games:
            if game.contains_users(p_1, p_2):
                contains_user = True
                break
        if not contains_user:
            games.append(Match(None, None, p_1, p_2, None))

used_times = []
for game in games:
    for match in matches:
        if game.contains_users(match.p1, match.p2) and match.time not in used_times:
            game.time = match.time
            game.day = match.day
            used_times.append(game.time)

for game in games:
    if game.time is None:
        print(f"Could not find a time for a match between {game.p1} and {game.p2}")

print("Games:")
for game in games:
    if game.time is None:
        continue
    print(f"{game.p1} vs {game.p2} will be at {game.time} on {game.day}")
