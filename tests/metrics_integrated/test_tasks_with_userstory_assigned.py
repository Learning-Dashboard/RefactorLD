from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["tasks"]

collection.delete_many({})

collection.insert_many([
    { "user_story_id": 100, "milestone_closed": False },
    { "user_story_id": 101, "milestone_closed": False },
    { "user_story_id": 102, "milestone_closed": False },
    { "user_story_id": 103, "milestone_closed": False },
    { "user_story_id": None, "milestone_closed": False },
    { "user_story_id": None, "milestone_closed": True }
])

expected_total = 5
expected_no_userstory = 1
expected_metric = 1 - (expected_no_userstory / expected_total)  # 1 - (1/5) = 0.8

pipeline = [
    {
        "$match": {
            "user_story_id": { "$exists": True },
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": None,
            "totalTasks": { "$sum": 1 },
            "tasksWithUserStoryNull": {
                "$sum": {
                    "$cond": [ { "$eq": ["$user_story_id", None] }, 1, 0 ]
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "totalTasks": 1,
            "tasksWithUserStoryNull": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalTasks"] == expected_total, f"Error: Total esperat {expected_total}, obtingut {result['totalTasks']}"
assert result["tasksWithUserStoryNull"] == expected_no_userstory, f"Error: Valor esperat {expected_no_userstory}, obtingut {result['tasksWithUserStoryNull']}"

metric = 1 - (result["tasksWithUserStoryNull"] / result["totalTasks"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")
