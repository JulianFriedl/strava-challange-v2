import logging
from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)

athlete_repo = AthleteRepository()
activity_repo = ActivityRepository()

def get_all_athlete_activities():
    """
    Fetch all activities from athlete and return aggregated result.
    """
    logger.info("Fetching all athletes.")

    athletes = athlete_repo.get_all_athletes()
    # IMPORTANT: keep mapped_types sorted by value!
    mapped_types = {
        "Ride": "Bike",
        "VirtualRide": "Bike",
        "Velomobile": "Bike",
        "Handcycle": "Bike",
        "Run": "Run",
        "VirtualRun": "Run",
        "BackcountrySki": "Hiking",
        "Hike": "Hiking",
        "Snowshoe": "Hiking",
        "AlpineSki": "Alpine Snow Sports",
        "Snowboard": "Alpine Snow Sports",
        "IceSkate": "Nordic Ski / Inline",
        "InlineSkate": "Nordic Ski / Inline",
        "NordicSki": "Nordic Ski / Inline",
        "RollerSki": "Nordic Ski / Inline",
        "Crossfit": "Gym",
        "WeightTraining": "Gym",
        "Workout": "Gym",
        "Soccer": "Ball Sports",
        "RockClimbing": "Climbing",
        "Kayaking": "Water Sports",
        "Kitesurf": "Water Sports",
        "Rowing": "Water Sports",
        "Sail": "Water Sports",
        "StandUpPaddling": "Water Sports",
        "Surfing": "Water Sports",
        "Swim": "Water Sports",
        "Windsurf": "Water Sports",
    }

    all = []
    last_type = ""
    subtype = []
    for t in mapped_types:
        if last_type == "":
            last_type = mapped_types[t]

        for a in athletes:
            activities = activity_repo.find_activities_by_athlete_and_type_with_year2025(a.athlete_id, t)
            points = calc_total_points(activities, mapped_types[t])
            moving_time = calc_total_moving_time(activities)

            # switch activity category pool
            if mapped_types[t] != last_type:
                subtype.sort(key=sort_func, reverse=True)
                all.append({"name": last_type, "rankings": subtype})
                subtype = []
                last_type = mapped_types[t]

            # insert new athlete to activity pool
            # or update athelte's points
            entry = next((x for x in subtype if x["username"] == a.username), [])
            if entry:
                subtype.remove(entry)
                subtype.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": entry["points"] + points, "mov": entry["mov"] + moving_time})
            else:
                subtype.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": points, "mov": moving_time})

    subtype.sort(key=sort_func, reverse=True)
    all.append({"name": last_type, "rankings": subtype})

    # add total ranking to list
    total = []
    for a in athletes:
        places = []
        for category in all:
            indices = [x for x in category["rankings"] if x["username"] == a.username]
            if indices[0]["points"] != 0:
                places.append({"rank": category["rankings"].index(indices[0]), "mov": indices[0]["mov"]})
        # sort places list for a better usage later when taking only the best 3 places
        places.sort(key=sort_func_2)

        sum = 0
        sum_mov = 0
        # take the best 3 places of an athlete and append the entry to the overall leaderboard
        for i in range(3):
            if i == len(places):
                break
            sum += 10 - places[i]["rank"]
            sum_mov += places[i]["mov"]
        total.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": sum, "mov": sum_mov})

    # sort overall leaderboard in search for a tie
    total = sort_overall_leaderboard(total)
    all.append({"name": "Overall", "rankings": total})

    return all

def calc_total_points(activities, grouped_type):
    """
    Function for calculating overall moving time in a specific category (grouped activities).
    For Alpine Snow Sports it aggregates the total elevation loss.
    """
    sum = 0
    for a in activities:
        if grouped_type == "Alpine Snow Sports":
            sum += a.total_elevation_gain
        else:
            sum += a.moving_time

    return sum

def calc_total_moving_time(activities):
    """
    Function for calculating overall moving time in a specific category (grouped activities).
    """
    sum = 0
    for a in activities:
        sum += a.moving_time

    return sum

def sort_overall_leaderboard(leaderboard):
    """
    
    """
    new_leaderboard = []
    for person in leaderboard:
        if new_leaderboard == []:
            new_leaderboard.append(person)
            continue

        i = 0
        while i < len(new_leaderboard) and (person["points"] < new_leaderboard[i]["points"] or (person["points"] == new_leaderboard[i]["points"] and person["mov"] < new_leaderboard[i]["mov"])):
            i += 1

        if i == len(new_leaderboard):
            new_leaderboard.append(person)
        else:
            new_leaderboard.insert(i, person)

    return new_leaderboard

def sort_func(e):
  """
  Sort function for points
  """
  return e['points']

def sort_func_2(e):
  """
  Sort function for ranks
  """
  return e['rank']
