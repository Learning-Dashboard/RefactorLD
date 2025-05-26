from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["issues"]

collection.delete_many({})

collection.insert_many([
    { "priority": "High" },
    { "priority": "High" },
    { "priority": "Low" },
    { "priority": "High" },
    { "priority": "Normal" }
])

expected_total = 5
expected_high = 3
expected_metric = 1 - (expected_high / expected_total)  # 1 - (3/5) = 0.4

pipeline = [
    {
        "$group": {
            "_id": None,
            "issuesTotal": { "$sum": 1 },
            "issuesHigh": {
                "$sum": {
                    "$cond": [
                        { "$eq": ["$priority", "High"] },
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
            "issuesTotal": 1,
            "issuesHigh": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["issuesTotal"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['issuesTotal']}"
assert result["issuesHigh"] == expected_high, f"Error: valor esperat {expected_high}, obtingut {result['issuesHigh']}"

metric = 1 - (result["issuesHigh"] / result["issuesTotal"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")