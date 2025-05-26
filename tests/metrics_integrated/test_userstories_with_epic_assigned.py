from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["userstories"]

collection.delete_many({})

collection.insert_many([
    { "epic_id": 1001, "milestone_closed": False },
    { "epic_id": 1002, "milestone_closed": False },
    { "epic_id": 1003, "milestone_closed": False },
    { "epic_id": 1004, "milestone_closed": False },
    { "epic_id": 1005, "milestone_closed": False },
    { "epic_id": None, "milestone_closed": False },
    { "epic_id": None, "milestone_closed": False },
    { "epic_id": None, "milestone_closed": True }
])

expected_total = 7
expected_no_epic = 2
expected_metric = 1 - (expected_no_epic / expected_total)  # 1 - (2/7) = 0.714

pipeline = [
    {
        "$match": {
            "epic_id": { "$exists": True },
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": None,
            "totalUserStories": { "$sum": 1 },
            "storiesWithEpicNull": {
                "$sum": {
                    "$cond": [ { "$eq": ["$epic_id", None] }, 1, 0 ]
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "totalUserStories": 1,
            "storiesWithEpicNull": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalUserStories"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['totalUserStories']}"
assert result["storiesWithEpicNull"] == expected_no_epic, f"Error: valor esperat {expected_no_epic}, obtingut {result['storiesWithEpicNull']}"

metric = 1 - (result["storiesWithEpicNull"] / result["totalUserStories"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")
