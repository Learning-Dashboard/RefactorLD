from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["commits"]

collection.delete_many({})

collection.insert_many([
    { "user": { "login": "anonymous" } },
    { "user": { "login": "anonymous" } },
    { "user": { "login": "anna_proba" } },
    { "user": { "login": "marc_proba" } },
    { "user": { "login": "laia_proba" } },
])

expected_commits_all = 5
expected_commit_anonymous = 2
expected_metric = 1 - (expected_commit_anonymous / expected_commits_all) # 1 - (2/5) = 0.6

pipeline = [
    {
        "$group": {
            "_id": None,
            "commitsAll": { "$sum": 1 },
            "commitAnonymous": {
                "$sum": {
                    "$cond": [
                        { "$eq": ["$user.login", "anonymous"] },
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
            "commitsAll": 1,
            "commitAnonymous": 1
        }
    }
]

# Resultat
result = list(collection.aggregate(pipeline))[0]

assert result["commitsAll"] == expected_commits_all, f"Error: commits totals esperats {expected_commits_all}, obtinguts {result['commitsAll']}"
assert result["commitAnonymous"] == expected_commit_anonymous, f"Error: commits anònims esperats {expected_commit_anonymous}, obtinguts {result['commitAnonymous']}"

metric = 1 - (result["commitAnonymous"] / result["commitsAll"])
assert math.isclose(metric, expected_metric, rel_tol=1e-4), f"Error: mètrica esperada {expected_metric}, obtinguda {metric}"

print(f"Test superat: Valor mètrica = {round(metric, 4)}")