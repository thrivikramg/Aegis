import os
from pymongo import MongoClient
from dotenv import load_dotenv

def clear_false_positive(target_prompt):
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI", __import__("base64").b64decode("bW9uZ29kYitzcnY6Ly90aHJpdmlrcmFtMzMwMTp2aWduZXNoQGNsdXN0ZXIwLmhyNXNqZjQubW9uZ29kYi5uZXQvP2FwcE5hbWU9Q2x1c3RlcjA=").decode("utf-8"))
    if not mongo_uri:
        print("MONGODB_URI not found in environment.")
        return

    client = MongoClient(mongo_uri)
    db = client["aegis_db"]
    
    # 1. Find the attack_id(s) for the prompt in the attacks collection
    attack_cursor = db["attacks"].find({"attack_prompt": target_prompt}, {"attack_id": 1})
    attack_ids = [doc["attack_id"] for doc in attack_cursor]
    
    if not attack_ids:
        # Try a substring match just in case
        print(f"No exact match for '{target_prompt}'. Searching for substrings...")
        attack_cursor = db["attacks"].find({"attack_prompt": {"$regex": target_prompt, "$options": "i"}}, {"attack_id": 1})
        attack_ids = [doc["attack_id"] for doc in attack_cursor]

    if not attack_ids:
        print(f"No records found for prompt: {target_prompt}")
        return

    # 2. Delete entries in defense_memory that reference these attack_ids
    result = db["defense_memory"].delete_many({"created_from_attack": {"$in": attack_ids}})
    
    print(f"Successfully removed {result.deleted_count} entries from Defense Memory related to '{target_prompt}'.")

if __name__ == "__main__":
    import sys
    prompt_to_clear = sys.argv[1] if len(sys.argv) > 1 else "hi"
    clear_false_positive(prompt_to_clear)
