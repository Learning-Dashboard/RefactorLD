from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["commits"]

collection.delete_many({})

collection.insert_many([
    { "user": { "login": "anna" } },
    { "user": { "login": "anna" } },
    { "user": { "login": "anna" } },
    { "user": { "login": "marc" } },
    { "user": { "login": "laia" } },
    { "user": { "login": "laia" } },
])

commits_per_user = [3, 1, 2]
expected_avg = sum(commits_per_user) / len(commits_per_user)
expected_stddev = math.sqrt(sum((x - expected_avg)**2 for x in commits_per_user) / len(commits_per_user))
expected_metric = 1 - (expected_stddev / expected_avg)

pipeline = [
    {
        "$match": {
            "user.login": { "$exists": True, "$ne": None }
        }
    },
    {
        "$group": {
            "_id": "$user.login",
            "commitsCount": { "$sum": 1 }
        }
    },
    {
        "$group": {
            "_id": None,
            "averageCommits": { "$avg": "$commitsCount" },
            "stdDevCommits": { "$stdDevPop": "$commitsCount" }
        }
    },
    {
        "$project": {
            "_id": 0,
            "averageCommits": 1,
            "stdDevCommits": 1
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert math.isclose(result["averageCommits"], expected_avg, rel_tol=1e-4), f"Mitjana esperada {expected_avg}, obtinguda {result['averageCommits']}"
assert math.isclose(result["stdDevCommits"], expected_stddev, rel_tol=1e-4), f"Desviació esperada {expected_stddev}, obtinguda {result['stdDevCommits']}"

metric = 1 - (result["stdDevCommits"] / result["averageCommits"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")
