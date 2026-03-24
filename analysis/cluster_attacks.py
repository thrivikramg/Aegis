import os
import sys
import numpy as np
from sklearn.cluster import DBSCAN

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

def run_clustering():
    db = Database()
    if not db.enabled: return
    
    print("[Clustering Engine] Fetching embedded attacks from Cloud Memory...")
    cursor = db.attacks.find({}, {"attack_id": 1, "embedding_vector": 1, "attack_prompt": 1})
    docs = list(cursor)
    
    valid_docs = [d for d in docs if d.get("embedding_vector")]
    if len(valid_docs) < 2:
        print("[Clustering Engine] Not enough high-fidelity data to execute topology clustering.")
        return
        
    embeddings = np.array([d["embedding_vector"] for d in valid_docs])
    ids = [d["attack_id"] for d in valid_docs]
    
    # Executes unsupervised clustering natively
    clustering = DBSCAN(eps=0.15, min_samples=2, metric="cosine").fit(embeddings)
    labels = clustering.labels_
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"[Clustering Engine] Mapping Complete. Found {n_clusters} emerging threat vectors.")
    
    # Async mass update routing back into the attacks telemetry
    for label, at_id in zip(labels, ids):
        if label != -1: # exclude noise points
            db._async_run(
                db.attacks.update_one,
                {"attack_id": at_id},
                {"$set": {"cluster_id": int(label)}}
            )
            
if __name__ == "__main__":
    run_clustering()
