from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["taiga_tasks"]

collection.delete_many({})

collection.insert_many([
    {"is_closed": True, "estimated_effort": 10, "actual_effort": 9, "milestone_closed": False},
    {"is_closed": True, "estimated_effort": 10, "actual_effort": 11, "milestone_closed": False},
    {"is_closed": True, "estimated_effort": 10, "actual_effort": 7, "milestone_closed": False},
    {"is_closed": True, "estimated_effort": 20, "actual_effort": 23, "milestone_closed": False},
    {"is_closed": True, "estimated_effort": 20, "actual_effort": 30, "milestone_closed": False},
    {"is_closed": True, "estimated_effort": 100, "actual_effort": 150, "milestone_closed": True},
])

threshold = 10
expected_total = 5 # hi ha una amb el milestone_closed = true
expected_high_deviated = 3
expected_metric = 1 - (expected_high_deviated / expected_total) # 1 - (3/5) = 0.4

pipeline = [
    {
        "$match": {
            "is_closed": True,
            "estimated_effort": { "$ne": None },
            "actual_effort": { "$ne": None },
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": None,
            "closedTasksWithEffortTotal": { "$sum": 1 },
            "highDeviatedTasks": {
                "$sum": {
                    "$cond": [
                        {
                            "$gt": [
                                { "$abs": { "$subtract": ["$actual_effort", "$estimated_effort"] }},
                                { "$multiply": ["$estimated_effort", threshold / 100] }
                            ]
                        },
                        1,
                        0
                    ]
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "closedTasksWithEffortTotal": 1,
            "highDeviatedTasks": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["closedTasksWithEffortTotal"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['closedTasksWithEffortTotal']}"
assert result["highDeviatedTasks"] == expected_high_deviated, f"Error: desviacions altes esperades {expected_high_deviated}, obtingudes {result['highDeviatedTasks']}"

metric = 1 - (result["highDeviatedTasks"] / result["closedTasksWithEffortTotal"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4),f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")
