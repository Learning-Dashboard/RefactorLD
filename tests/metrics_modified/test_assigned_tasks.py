from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["taiga_tasks"]

collection.delete_many({})

collection.insert_many([
    { "assigned": "anna", "milestone_closed": False },
    { "assigned": "marc", "milestone_closed": False },
    { "assigned": None, "milestone_closed": False },
    { "assigned": "", "milestone_closed": False },
    { "assigned": None, "milestone_closed": True },
])

expected_total = 4
expected_unassigned = 2
expected_metric = 1 - (expected_unassigned / expected_total)  # 1 - (2/4) = 0.5

pipeline = [
    {
        "$match": {
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": None,
            "tasksTotal": { "$sum": 1 },
            "tasksUnassigned": {
                "$sum": {
                    "$cond": [
                        { "$or": [
                            { "$eq": ["$assigned", None] },
                            { "$eq": ["$assigned", ""] }
                        ]},
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
            "tasksTotal": 1,
            "tasksUnassigned": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["tasksTotal"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['tasksTotal']}"
assert result["tasksUnassigned"] == expected_unassigned, f"Error: tasques no assignades esperades {expected_unassigned}, obtingudes {result['tasksUnassigned']}"

metric = 1 - (result["tasksUnassigned"] / result["tasksTotal"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")
