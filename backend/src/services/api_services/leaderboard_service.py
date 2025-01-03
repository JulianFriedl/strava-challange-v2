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
            points = calc_total_time(activities, mapped_types[t])
            if mapped_types[t] != last_type:
                subtype.sort(key=sort_func, reverse=True)
                all.append({"name": last_type, "rankings": subtype})
                subtype = []
                last_type = mapped_types[t]

            entry = next((x for x in subtype if x["username"] == a.username), [])
            if entry:
                subtype.remove(entry)
                subtype.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": entry["points"] + points})
            else:
                subtype.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": points})

    subtype.sort(key=sort_func, reverse=True)
    all.append({"name": last_type, "rankings": subtype})

    # add total ranking to list
    total = []
    for a in athletes:
        places = []
        for category in all:
            indices = [x for x in category["rankings"] if x["username"] == a.username]
            if indices[0]["points"] != 0:
                places.insert(0, category["rankings"].index(indices[0]))
        places.sort()

        sum = 0
        for i in range(3):
            if i == len(places):
                break
            sum += 10 - places[i]
        total.append({"username": a.username, "name": a.first_name + " " + a.last_name, "points": sum})

    total.sort(key=sort_func, reverse=True)
    all.append({"name": "Overall", "rankings": total})

    return all

def calc_total_time(activities, grouped_type):
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

def sort_func(e):
  """
  Sort function for points
  """
  return e['points']
