from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["pr"]

collection.delete_many({})

collection.insert_many([
    { "reviewers": ["anna"] },
    { "reviewers": ["jordi"] },
    { "reviewers": None },
    { "reviewers": None },
    { "reviewers": ["carla"] },
    { "reviewers": ["anna"] },
    { "reviewers": ["anna"] },
    { "reviewers": ["carla"] },
    { "reviewers": None },
])

expected_total = 9
expected_without_reviewers = 3
expected_metric = 1 - (expected_without_reviewers / expected_total)  # 1 - (3/9) = 1 - 0.33 = 0.667

pipeline = [
    {
        "$group": {
            "_id": None,
            "totalPRs": { "$sum": 1 },
            "prsWithoutReviewer": {
                "$sum": {
                    "$cond": [
                        {
                            "$or": [
                                { "$eq": ["$reviewers", None] },
                                { "$eq": ["$reviewers", []] }
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
            "totalPRs": 1,
            "prsWithoutReviewer": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert result["totalPRs"] == expected_total, f"Error: total esperat {expected_total}, obtingut {result['totalPRs']}"
assert result["prsWithoutReviewer"] == expected_without_reviewers,f"Error: valor esperat {expected_without_reviewers}, obtingut {result['prsWithoutReviewer']}"

metric = 1 - (result["prsWithoutReviewer"] / result["totalPRs"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4),f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor metrica = {round(metric, 4)}")
