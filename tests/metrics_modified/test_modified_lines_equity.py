from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["commits"]

collection.delete_many({})

collection.insert_many([
    { "user": { "login": "anna" }, "stats": { "total": 120 } },
    { "user": { "login": "anna" }, "stats": { "total": 80 } },
    { "user": { "login": "marc" }, "stats": { "total": 100 } },
    { "user": { "login": "laia" }, "stats": { "total": 50 } },
    { "user": { "login": "laia" }, "stats": { "total": 50 } },
])

modified_lines_per_user = [200, 100, 100]
expected_avg = sum(modified_lines_per_user) / len(modified_lines_per_user)
expected_stddev = math.sqrt(sum((x - expected_avg)**2 for x in modified_lines_per_user) / len(modified_lines_per_user))
expected_metric = 1 - (expected_stddev / expected_avg)

pipeline = [
    {
        "$match": {
            "user.login": { "$exists": True, "$ne": None },
            "stats.total": { "$exists": True }
        }
    },
    {
        "$group": {
            "_id": "$user.login",
            "modifiedLines": { "$sum": "$stats.total" }
        }
    },
    {
        "$group": {
            "_id": None,
            "averageModifiedLines": { "$avg": "$modifiedLines" },
            "stdDevModifiedLines": { "$stdDevPop": "$modifiedLines" }
        }
    },
    {
        "$project": {
            "_id": 0,
            "averageModifiedLines": 1,
            "stdDevModifiedLines": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert math.isclose(result["averageModifiedLines"], expected_avg, rel_tol=1e-4), f"Mitjana esperada {expected_avg}, obtinguda {result['averageModifiedLines']}"

assert math.isclose(result["stdDevModifiedLines"], expected_stddev, rel_tol=1e-4), f"Desviació esperada {expected_stddev}, obtinguda {result['stdDevModifiedLines']}"

metric = 1 - (result["stdDevModifiedLines"] / result["averageModifiedLines"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Mètrica esperada {expected_metric}, obtinguda {metric}"
print(f"Test superat: Valor mètrica = {round(metric, 4)}")
