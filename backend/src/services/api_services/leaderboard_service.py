import logging
import math
from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)

# IMPORTANT: keep mapped_types sorted by value!
mapped_types = {
    "Ride": "Biking",
    "VirtualRide": "Biking",
    "Velomobile": "Biking",
    "Handcycle": "Biking",
    "GravelRide": "Biking",
    "MountainBikeRide": "Biking",
    "Run": "Running",
    "VirtualRun": "Running",
    "TrailRun": "Running",
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
    "HighIntensityIntervalTraining": "Gym",
    "Soccer": "Ball Sports",
    "Badminton": "Ball Sports",
    "Pickleball": "Ball Sports",
    "Racquetball": "Ball Sports",
    "Squash": "Ball Sports",
    "TableTennis": "Ball Sports",
    "Tennis": "Ball Sports",
    "RockClimbing": "Climbing",
    "Kayaking": "Water Sports",
    "Kitesurf": "Water Sports",
    "Windsurf": "Water Sports",
    "Rowing": "Water Sports",
    "VirtualRow": "Water Sports",
    "Sail": "Water Sports",
    "Canoeing": "Water Sports",
    "StandUpPaddling": "Water Sports",
    "Surfing": "Water Sports",
    "Swim": "Water Sports",
    "Windsurf": "Water Sports",
}

def get_full_leaderboard():
    """
    Fetch all activities from athlete and return aggregated result.
    """
    athlete_repo = AthleteRepository()
    activity_repo = ActivityRepository()
    logger.debug("Fetching all athletes.")

    athletes = athlete_repo.get_all_athletes()

    logger.debug("Start calculating rankings for each category.")
    all = [] # [{name: Biking, rankings: [athlete, athlete, ...]}, {name, rankings}, ...]
    last_type = ""
    category = [] # [athelete with points, another athlete with points, ...]
    for t in mapped_types:
        if last_type == "":
            last_type = mapped_types[t]

        # switch activity category pool
        if mapped_types[t] != last_type:
            category.sort(key=lambda x: x["points"], reverse=True)
            all.append({"name": last_type, "rankings": category})
            category = []
            last_type = mapped_types[t]

        for a in athletes:
            activities = activity_repo.find_activities_by_athlete_and_type_with_year2025(a.athlete_id, t)
            moving_time = calc_total_moving_time(activities)

            # insert new athlete to activity pool
            # or update athelte's points
            entry = next((x for x in category if x["id"] == a.athlete_id), [])
            if entry:
                category.remove(entry)
                category.append({"id": a.athlete_id, "name": a.first_name + " " + a.last_name, "points": entry["points"] + moving_time})
            else:
                category.append({"id": a.athlete_id, "name": a.first_name + " " + a.last_name, "points": moving_time})

    category.sort(key=lambda x: x["points"], reverse=True)
    all.append({"name": last_type, "rankings": category})

    # Calculate activity factors
    category_totals = {category["name"]: sum(entry["points"] for entry in category["rankings"]) for category in all}
    factors = calculate_activity_factor(category_totals)
    for category, factor in factors.items():
        logger.debug(f"Category: {category}, Factor: {factor:.2f}")

    # add total ranking to list
    logger.debug("Add overall leaderboard to rankings.")
    total = [] # equal to category
    for a in athletes:
        places = []
        for cat in all:
            indices = [x for x in cat["rankings"] if x["id"] == a.athlete_id]
            if indices[0]["points"] != 0:
                places.append({"rank": cat["rankings"].index(indices[0]), "mov": indices[0]["points"], "category": cat["name"]})
        # sort places list for a better usage later when taking only the best 3 places
        places.sort(key=lambda x: x["rank"])

        # multiply rankings by category specific factor
        total_points = 0
        sum_mov = 0
        for place in places:
            factor = factors.get(place["category"], 1)
            adjusted_points = round((10 - place["rank"]) * factor, 1)
            place["adjusted_points"] = adjusted_points

        places.sort(key=lambda x: x["adjusted_points"], reverse=True)

        # Pick the top 3 places that maximize points
        for i in range(3):
            if i >= len(places):
                break
            place = places[i]
            total_points += place["adjusted_points"]
            sum_mov += place["mov"]

        # Append the athlete's result to the total leaderboard
        total.append({
            "username": a.username,
            "name": a.first_name + " " + a.last_name,
            "points": total_points,
            "mov": sum_mov
        })

    # sort overall leaderboard in search for a tie
    total = sort_overall_leaderboard(total)
    all.append({"name": "Overall", "rankings": total})

    return all

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
    Function for sorting the overall leaderboard. This is diffferent then pythons sort function since there has to be differentiation if two athletes have equal points.
    """
    new_leaderboard = []
    for person in leaderboard:
        if new_leaderboard == []:
            new_leaderboard.append(person)
            continue

        i = 0
        # move counter (i) to the specific location where the athlete has to be inserted
        while i < len(new_leaderboard) and (person["points"] < new_leaderboard[i]["points"]
                                            or (person["points"] == new_leaderboard[i]["points"]
                                                and person["mov"] < new_leaderboard[i]["mov"])):
            i += 1

        # if the athelete has the least points, just append the list
        if i == len(new_leaderboard):
            new_leaderboard.append(person)
        else:
            new_leaderboard.insert(i, person)

    return new_leaderboard


def calculate_activity_factor(activity_times, min_factor=0.75, max_factor=1.25):
    """
    Calculate a factor for each category based on total activity time.
    """
    if not activity_times:
        return {}

    min_time = min(activity_times.values())
    max_time = max(activity_times.values())

    if min_time == max_time:
        return {category: (min_factor + max_factor) / 2 for category in activity_times}

    factors = {
        category: min_factor + (max_factor - min_factor) * (time - min_time) / (max_time - min_time)
        for category, time in activity_times.items()
    }
    return factors
