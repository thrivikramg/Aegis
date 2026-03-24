import numpy as np
import uuid
from sklearn.cluster import DBSCAN
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

class EmergingThreatAnalyzer:
    """Background Daemon clustering raw cloud memories mathematically into Threat Intelligence objects."""
    def __init__(self, db):
        self.db = db
        
    def discover_patterns(self):
        """Unsupervised clustering measuring explicit density vectors to isolate dynamic threats."""
        if not self.db or not self.db.enabled: return
        print("[Threat Intelligence] Orchestrating Unsupervised Threat Aggregation...")
        
        cursor = self.db.attacks.find({}, {"attack_prompt": 1, "embedding_vector": 1})
        valid = [d for d in list(cursor) if d.get("embedding_vector") and len(d.get("embedding_vector")) > 0]
        
        if len(valid) < 3: 
            print("[Threat Intelligence] Extracted Telemetry volume insufficient for topology scanning.")
            return
            
        embeddings = np.array([d["embedding_vector"] for d in valid])
        prompts = [d["attack_prompt"] for d in valid]
        
        clustering = DBSCAN(eps=0.15, min_samples=2, metric="cosine").fit(embeddings)
        labels = clustering.labels_
        
        from collections import Counter
        counts = Counter([l for l in labels if l != -1]) # Ignore noise topology points (-1)
        
        for cluster_label, count in counts.items():
            if count >= 2:
                indices = [i for i, l in enumerate(labels) if l == cluster_label]
                rep_prompt = prompts[indices[0]]
                
                self.db.log_threat_cluster({
                    "cluster_id": f"tc-{uuid.uuid4().hex[:8]}",
                    "attack_count": count,
                    "growth_rate": "high",
                    "representative_prompt": rep_prompt,
                    "risk_level": "Critical" if count > 5 else "Warning"
                })
        print(f"[Threat Intelligence] Successfully tracked {len(counts)} converging adversarial grids natively.")
        
if __name__ == "__main__":
    db = Database()
    analyzer = EmergingThreatAnalyzer(db)
    analyzer.discover_patterns()
