from pymongo import MongoClient
from datetime import datetime
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["issues"]

collection.delete_many({})

collection.insert_many([
    {
        "is_closed": True,
        "created_date": datetime(2024, 4, 1),
        "finished_date": datetime(2024, 4, 7)  # 6 dies
    },
    {
        "is_closed": True,
        "created_date": datetime(2024, 4, 1),
        "finished_date": datetime(2024, 4, 8)  # 7 dies
    },
    {
        "is_closed": True,
        "created_date": datetime(2024, 4, 1),
        "finished_date": datetime(2024, 4, 9)  # 8 dies
    },
    {
        "is_closed": True,
        "created_date": datetime(2024, 4, 1),
        "finished_date": datetime(2024, 4, 12)  # 11 dies
    }
])

expected_total = 4      # 4 issues en total
expected_avg = 8.0      # (6+7+8+11)/4 = 32/4 = 8
expected_normalitzacio = 0.75   # per la normalització: 8 dies = 0.75

pipeline = [
    {
        "$match": {
            "is_closed": True,
            "created_date": { "$exists": True, "$ne": None },
            "finished_date": { "$exists": True, "$ne": None }
        }
    },
    {
        "$project": {
            "resolutionTimeDays": {
                "$divide": [
                    { "$subtract": [
                        { "$toDate": "$finished_date" },
                        { "$toDate": "$created_date" }
                    ]},
                    86400000
                ]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "totalIssues": { "$sum": 1 },
            "avgResolutionTime": { "$avg": "$resolutionTimeDays" }
        }
    },
    {
        "$project": {
            "_id": 0,
            "totalIssues": 1,
            "avgResolutionTime": 1,
            "normalizedResolutionScore": {
                "$switch": {
                    "branches": [
                        { "case": { "$lte": ["$avgResolutionTime", 7] }, "then": 1.0 },
                        { "case": { "$and": [ { "$gt": ["$avgResolutionTime", 7] }, { "$lte": ["$avgResolutionTime", 8] } ] }, "then": 0.75 },
                        { "case": { "$and": [ { "$gt": ["$avgResolutionTime", 8] }, { "$lte": ["$avgResolutionTime", 9] } ] }, "then": 0.5 },
                        { "case": { "$and": [ { "$gt": ["$avgResolutionTime", 9] }, { "$lte": ["$avgResolutionTime", 10] } ] }, "then": 0.25 }
                    ],
                    "default": 0.0
                }
            }
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalIssues"] == expected_total, f"Error: Total esperat: {expected_total}, obtingut: {result['totalIssues']}"
assert math.isclose(result["avgResolutionTime"], expected_avg, rel_tol=1e-4),f"Error: Promig esperat: {expected_avg}, obtingut: {result['avgResolutionTime']}"
assert result["normalizedResolutionScore"] == expected_normalitzacio,f"Error: Valor esperat: {expected_normalitzacio}, obtingut: {result['normalizedResolutionScore']}"

print(f"Test superat: Mitjana de dies = {result['avgResolutionTime']:.2f} dies. Valor metrica (normalitzat) = {result['normalizedResolutionScore']}")
