from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["tasks"]

collection.delete_many({})

def gen_tasks(user, count, milestone_closed=False):
    return [{ "assigned": user, "milestone_closed": milestone_closed } for _ in range(count)]

tasks = (
    gen_tasks("anna", 49, milestone_closed=False) +
    gen_tasks("carla", 39, milestone_closed=False) +
    gen_tasks("jordi", 43, milestone_closed=False) +
    gen_tasks("marc", 44, milestone_closed=False) +
    gen_tasks("ignorada", 20, milestone_closed=True)  # Aquestes no s'han de comptar
)

collection.insert_many(tasks)

tasks_counts = [49, 39, 43, 44]
average = sum(tasks_counts) / len(tasks_counts)
squared_diffs = [(x - average) ** 2 for x in tasks_counts]
std_dev = (sum(squared_diffs) / len(tasks_counts)) ** 0.5
expected_equity = 1 - (std_dev / average)

pipeline = [
    {
        "$match": {
            "assigned": { "$exists": True, "$ne": None },
            "milestone_closed": False
        }
    },
    {
        "$group": {
            "_id": "$assigned",
            "tasksCount": { "$sum": 1 }
        }
    },
    {
        "$group": {
            "_id": None,
            "averageTasks": { "$avg": "$tasksCount" },
            "stdDevTasks": { "$stdDevPop": "$tasksCount" }
        }
    },
    {
        "$project": {
            "_id": 0,
            "averageTasks": 1,
            "stdDevTasks": 1,
            "equityScore": {
                "$cond": [
                    { "$eq": ["$averageTasks", 0] },
                    1.0,
                    { "$subtract": [1, { "$divide": ["$stdDevTasks", "$averageTasks"] }] }
                ]
            }
        }
    }
]

result = list(collection.aggregate(pipeline))[0]
assert math.isclose(result["averageTasks"], average, rel_tol=1e-5), f"Error: mitjana esperada {average}, obtinguda {result['averageTasks']}"
assert math.isclose(result["stdDevTasks"], std_dev, rel_tol=1e-5), f"Error: desviació esperada {std_dev}, obtinguda {result['stdDevTasks']}"
assert math.isclose(result["equityScore"], expected_equity, rel_tol=1e-5), f"Error: equityScore esperat {expected_equity}, obtingut {result['equityScore']}"

print(f"Test superat: equityScore = {round(result['equityScore'], 4)}")
