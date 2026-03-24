from sklearn.ensemble import RandomForestClassifier
import numpy as np
import os
import pickle

class AttackBehaviorModel:
    """Predictive ML model utilizing Sklearn Forest arrays to infer zero day behavioural intent dynamically"""
    def __init__(self, db):
        self.db = db
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'behavior_rf.pkl'))
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)

    def extract_features(self, prompt: str, embedding: list, similarity: float) -> np.ndarray:
        length = len(prompt)
        words = len(prompt.split())
        instruct_flags = sum(1 for w in ["ignore", "system", "prompt", "forget", "act", "roleplay", "pretend"] if w in prompt.lower())
        
        features = [length, words, instruct_flags, similarity]
        # Project embedding telemetry (first 10 features natively)
        features.extend(embedding[:10] if embedding and len(embedding) >= 10 else [0.0]*10)
        return np.array(features).reshape(1, -1)
        
    def train(self):
        """Pulls stored telemetry directly from Sentinel Mongo logs to cross-train an internal heuristic framework."""
        if not self.db or not self.db.enabled: return
        print("[ML Engine] Training Behavioral Attack Random Forest...")
        
        cursor = self.db.attacks.find({}, {"attack_prompt": 1, "embedding_vector": 1, "similarity_score": 1, "success": 1})
        docs = list(cursor)
        
        if len(docs) < 5:
            print("[ML Engine] Minimum telemetry thresholds not met (<5 rows). Supervised model standing by.")
            return
            
        X, y = [], []
        for d in docs:
            if "attack_prompt" not in d: continue
            feat = self.extract_features(d["attack_prompt"], d.get("embedding_vector", []), d.get("similarity_score", 0.0))
            X.append(feat[0])
            
            # Map malicious class natively to similarity parameters and objective success indicators
            is_malicious = 1 if d.get("similarity_score", 0.0) > 0.4 or not d.get("success", True) else 0
            y.append(is_malicious)
            
        # Hardcoded semantic baselines (synthetic dataset normalization vectors)
        X.append(self.extract_features("hello how are you", [0.1]*10, 0.0)[0])
        y.append(0)
        X.append(self.extract_features("what is the weather currently", [0.05]*10, 0.0)[0])
        y.append(0)
            
        clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        clf.fit(X, y)
        self.model = clf
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print("[ML Engine] Random Forest array compiled and serialized identically.")

    def predict(self, prompt: str, embedding: list, similarity: float) -> float:
        if self.model is None:
            return 0.0
        try:
            feats = self.extract_features(prompt, embedding, similarity)
            prob = self.model.predict_proba(feats)[0][1] # Probability of class 1 (Attack)
            return float(prob)
        except Exception:
            return 0.0
