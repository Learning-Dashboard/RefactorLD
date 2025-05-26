from pymongo import MongoClient
import math

client = MongoClient("mongodb://admin:3LnS985q7tR9@localhost:27017")
db = client["test_ld"]
collection = db["tasks"]
collection.delete_many({})

def gen_tasks(user, actual_effort, milestone_closed):
    return [{ "assigned": user, "actual_effort": actual_effort, "milestone_closed": milestone_closed }]

tasks = (
    gen_tasks("anna", 7, False) +
    gen_tasks("anna", 3, False) +
    gen_tasks("carla", 10, False) +
    gen_tasks("jordi", 5, False) +
    gen_tasks("jordi", 5, False) +
    gen_tasks("marc", 15, False) +
    gen_tasks("marc", None, False) +
    gen_tasks("anna", 150, True)
)

collection.insert_many(tasks)

tasks_efforts = [10, 10, 10, 15]
expected_average = sum(tasks_efforts) / len(tasks_efforts)
expected_stddev = math.sqrt(sum((x - expected_average) ** 2 for x in tasks_efforts) / len(tasks_efforts))
effort_coverage_ratio = 6 / 7
expected_final_result = 1 - (expected_stddev / expected_average) if effort_coverage_ratio >= 0.75 else 0

pipeline = [
    {
        "$facet": {
            "effortStats": [
                {
                    "$match": {
                        "actual_effort": { "$ne": None },
                        "assigned": { "$ne": None },
                        "milestone_closed": False
                    }
                },
                {
                    "$group": {
                        "_id": "$assigned",
                        "effort": { "$sum": "$actual_effort" }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "averageEffort": { "$avg": "$effort" },
                        "stdDevEffort": { "$stdDevPop": "$effort" }
                    }
                }
            ],
            "coverage": [
                {
                    "$match": {
                        "milestone_closed": False
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "totalTasks": { "$sum": 1 },
                        "tasksWithEffort": {
                            "$sum": {
                                "$cond": [{ "$ne": ["$actual_effort", None] }, 1, 0]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "tasksWithActualEffort": {
                            "$cond": [
                                { "$eq": ["$totalTasks", 0] },
                                0,
                                { "$divide": ["$tasksWithEffort", "$totalTasks"] }
                            ]
                        }
                    }
                }
            ]
        }
    },
    {
        "$project": {
            "averageEffort": { "$arrayElemAt": ["$effortStats.averageEffort", 0] },
            "stdDevEffort": { "$arrayElemAt": ["$effortStats.stdDevEffort", 0] },
            "tasksWithActualEffort": { "$arrayElemAt": ["$coverage.tasksWithActualEffort", 0] },
            "finalResult": {
                "$cond": [
                    {
                        "$lt": [
                            { "$arrayElemAt": ["$coverage.tasksWithActualEffort", 0] }, 0.75
                        ]
                    },
                    0,
                    {
                        "$subtract": [
                            1,
                            {
                                "$divide": [
                                    { "$arrayElemAt": ["$effortStats.stdDevEffort", 0] },
                                    { "$arrayElemAt": ["$effortStats.averageEffort", 0] }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
]

result = list(collection.aggregate(pipeline))[0]

assert math.isclose(result["averageEffort"], expected_average, rel_tol=1e-5), f"Mitjana esperada: {expected_average}, obtinguda: {result['averageEffort']}"
assert math.isclose(result["stdDevEffort"], expected_stddev, rel_tol=1e-5), f"Desviació esperada: {expected_stddev}, obtinguda: {result['stdDevEffort']}"
assert math.isclose(result["tasksWithActualEffort"], effort_coverage_ratio, rel_tol=1e-5), f"Proporció amb effort esperada: {effort_coverage_ratio}, obtinguda: {result['tasksWithActualEffort']}"
assert math.isclose(result["finalResult"], expected_final_result, rel_tol=1e-5), f"Resultat final esperat: {expected_final_result}, obtingut: {result['finalResult']}"

print(f"Test superat: finalResult = {round(result['finalResult'], 4)}")
