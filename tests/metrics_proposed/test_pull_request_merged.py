from pymongo import MongoClient
from datetime import datetime, timedelta
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["pr"]

collection.delete_many({})

now = datetime.now()
collection.insert_many([
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": False},
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": False },
    { "closed_date": now, "merged": False },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True },
    { "closed_date": now, "merged": True }
])

expected_total = 12
expected_merged = 9
expected_metric = expected_merged / expected_total  # 9 / 12 = 0,75

pipeline = [
    {
        "$match": {
            "closed_date": { "$exists": True, "$ne": None }
        }
    },
    {
        "$group": {
            "_id": None,
            "totalPRs": { "$sum": 1 },
            "acceptedPRs": {
                "$sum": {
                    "$cond": [
                        { "$eq": ["$merged", True] },
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
            "acceptedPRs": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalPRs"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['totalPRs']}"
assert result["acceptedPRs"] == expected_merged,f"Error: valor esperat {expected_merged}, obtingut {result['acceptedPRs']}"

metric = result["acceptedPRs"] / result["totalPRs"]
assert math.isclose(metric, expected_metric, rel_tol=1e-4),f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor metrica = {round(metric, 4)}")
