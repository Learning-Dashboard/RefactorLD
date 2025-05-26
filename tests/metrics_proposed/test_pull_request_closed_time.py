from pymongo import MongoClient
from datetime import datetime, timedelta
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["pr"]

collection.delete_many({})

now = datetime.now()
collection.insert_many([
    { "creation_date": now - timedelta(days=3), "closed_date": now },
    { "creation_date": now - timedelta(days=5), "closed_date": now },
    { "creation_date": now - timedelta(days=1), "closed_date": now },
    { "creation_date": now - timedelta(days=6), "closed_date": now },
    { "creation_date": now - timedelta(days=10), "closed_date": now },
    { "creation_date": now - timedelta(days=8), "closed_date": now },
])

expected_total = 6
expected_over_7 = 2
expected_metric = 1 - (expected_over_7 / expected_total)  # 1 - (2/6) = 1 - 0.33 = 0.667

pipeline = [
    {
        "$match": {
            "closed_date": { "$exists": True, "$ne": None },
            "creation_date": { "$exists": True, "$ne": None }
        }
    },
    {
        "$project": {
            "durationDays": {
                "$divide": [
                    { "$subtract": [ "$closed_date", "$creation_date" ] },
                    1000 * 60 * 60 * 24
                ]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "totalPRs": { "$sum": 1 },
            "prsOver7Days": {
                "$sum": {
                    "$cond": [
                        { "$gt": ["$durationDays", 7] },
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
            "totalPRs": 1,
            "prsOver7Days": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalPRs"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['totalPRs']}"
assert result["prsOver7Days"] == expected_over_7,f"Error: valor esperat {expected_over_7}, obtingut {result['prsOver7Days']}"

metric = 1 - (result["prsOver7Days"] / result["totalPRs"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4),f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor metrica = {round(metric, 4)}")
