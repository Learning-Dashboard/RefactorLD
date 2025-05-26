from pymongo import MongoClient
from datetime import datetime
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["commits"]

collection.delete_many({})

USERNAME = "anna_proba"

collection.insert_many([
    { "user": { "login": USERNAME }, "date": datetime(2024, 4, 1, 23, 30) },
    { "user": { "login": USERNAME }, "date": datetime(2024, 4, 1, 10, 0) },
    { "user": { "login": USERNAME }, "date": datetime(2024, 4, 1, 12, 15) },
    { "user": { "login": USERNAME }, "date": datetime(2024, 4, 1, 18, 45) },
])

expected_total = 4
expected_out_of_hours = 1
expected_metric = 1-(expected_out_of_hours / expected_total)

pipeline = [
    { "$match": { "user.login": USERNAME } },
    { "$project": { "hour": { "$hour": { "$toDate": "$date" } } } },
    {
        "$group": {
            "_id": None,
            "commitsTotal": { "$sum": 1 },
            "commitsOutOfHours": {
                "$sum": {
                    "$cond": [
                        { "$or": [
                            { "$lt": ["$hour", 8] },
                            { "$gte": ["$hour", 20] }
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
            "commitsTotal": 1,
            "commitsOutOfHours": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["commitsTotal"] == expected_total, f"Error: commits totals esperats {expected_total}, obtinguts {result['commitsTotal']}"
assert result["commitsOutOfHours"] == expected_out_of_hours, f"Error: commits fora d'horari esperats {expected_out_of_hours}, obtinguts {result['commitsOutOfHours']}"

metric = 1 - (result["commitsOutOfHours"] / result["commitsTotal"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor metrica = {round(metric, 4)}")
