from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["tasks"]

collection.delete_many({})

collection.insert_many([
    { "is_closed": True,  "assigned": "anna",  "milestone_closed": False },
    { "is_closed": True,  "assigned": "jordi", "milestone_closed": False },
    { "is_closed": True,  "assigned": "jordi", "milestone_closed": False },
    { "is_closed": True,  "assigned": None,    "milestone_closed": False },
    { "is_closed": True,  "assigned": "carla", "milestone_closed": False },
    { "is_closed": True,  "assigned": "carla", "milestone_closed": False },
    { "is_closed": True,  "assigned": "carla", "milestone_closed": False },
    { "is_closed": True,  "assigned": "anna",  "milestone_closed": False },
    { "is_closed": True,  "assigned": "jordi", "milestone_closed": False },
    { "is_closed": True,  "assigned": "anna",  "milestone_closed": False },
    { "is_closed": True,  "assigned": "anna",  "milestone_closed": False },
    { "is_closed": True,  "assigned": "jordi", "milestone_closed": False },
    { "is_closed": True,  "assigned": None,    "milestone_closed": False },
    { "is_closed": True,  "assigned": "carla", "milestone_closed": False },
    { "is_closed": True,  "assigned": "anna",  "milestone_closed": True }
])

expected_total = 14
expected_assigned = 12
expected_metric = expected_assigned / expected_total  # 12 / 14 = 0.857

pipeline = [
    {
        "$match": {
            "is_closed": True,
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": None,
            "closedTasksTotal": { "$sum": 1 },
            "closedTasksAssigned": {
                "$sum": {
                    "$cond": [
                        {
                            "$and": [
                                { "$eq": ["$is_closed", True] },
                                { "$ne": ["$assigned", None] },
                                { "$ne": ["$assigned", ""] }
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
            "closedTasksTotal": 1,
            "closedTasksAssigned": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["closedTasksTotal"] == expected_total, f"Error: Total esperat {expected_total}, obtingut {result['closedTasksTotal']}"
assert result["closedTasksAssigned"] == expected_assigned, f"Error: Assignades esperades {expected_assigned}, obtingudes {result['closedTasksAssigned']}"

metric = result["closedTasksAssigned"] / result["closedTasksTotal"]
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: Mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")