from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['mediconnect_db']

collections = ['chat_logs', 'injury_logs', 'recovery_plans', 'emergency_logs']

for col in collections:
    result = db[col].update_many(
        {'user_id': 'user_001'},
        {'$set': {'user_id': '1532dd7b9333'}}
    )
    print(f'{col}: updated {result.modified_count} documents')

print('Done!')