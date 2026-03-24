import os
import sys
import json
import csv
import datetime
from bson import json_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

class DatasetExporter:
    """Artifact compiler converting live internal Mongo telemetry directly into serialized research formats like JSONL."""
    def __init__(self, db=None):
        self.db = db or Database()
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def export_telemetry(self):
        if not self.db.enabled: return
        print(f"[Exporter] Structuring deep memory arrays safely into `{self.output_dir}`...")
        
        attacks = list(self.db.attacks.find())
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
        
        # 1. Direct API Dump
        json_path = os.path.join(self.output_dir, f"aegis_attacks_{stamp}.json")
        with open(json_path, 'w') as f:
            f.write(json_util.dumps(attacks, indent=4))
            
        # 2. DataFrame/Pandas Formatted Artifact
        csv_path = os.path.join(self.output_dir, f"aegis_attacks_{stamp}.csv")
        if attacks:
            keys = ["attack_id", "attack_prompt", "attack_type", "success", "risk_score"]
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(attacks)
                
        # 3. HuggingFace specific (.jsonl) Structure natively
        hf_path = os.path.join(self.output_dir, f"hf_dataset_{stamp}.jsonl")
        with open(hf_path, 'w', encoding='utf-8') as f:
            for a in attacks:
                hf_obj = {
                    "text": a.get("attack_prompt", ""),
                    "label": "jailbreak" if a.get("success") else "benign",
                    "metadata": {"signature_class": a.get("attack_type"), "risk_variance": a.get("risk_score")}
                }
                f.write(json.dumps(hf_obj) + '\n')
                
        print("[Exporter] Database volumes strictly parsed securely.")

if __name__ == "__main__":
    exp = DatasetExporter()
    exp.export_telemetry()
