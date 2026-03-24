import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database
from analysis.attack_graph import AttackGraphModeler

class ThreatFeedGenerator:
    """Continuous automated reporting agent disseminating Sentinel intelligence artifacts natively."""
    def __init__(self, db):
        self.db = db
        
    def generate_weekly_report(self, output_dir="reports"):
        if not self.db or not self.db.enabled: return
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"[Intelligence Aggregator] Compiling Unified V4 SentinelLLM Executive Assessment...")
        
        total_attacks = self.db.attacks.count_documents({})
        bypasses = self.db.attack_outcomes.count_documents({"success": True})
        
        # Frequency Volumes
        pipeline = [{"$group": {"_id": "$attack_type", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 5}]
        top_types = list(self.db.attacks.aggregate(pipeline))
        
        # Vendor Breakdowns
        vuln_pipeline = [
            {"$match": {"success": True}},
            {"$lookup": {"from": "model_responses", "localField": "attack_id", "foreignField": "attack_id", "as": "resp"}},
            {"$unwind": "$resp"},
            {"$group": {"_id": "$resp.model_name", "bypasses": {"$sum": 1}}},
            {"$sort": {"bypasses": -1}}
        ]
        vuln_models = list(self.db.attack_outcomes.aggregate(vuln_pipeline))
        
        # Graph Execution (Tracing deepest mutations scaling Sentinel boundaries)
        graph_engine = AttackGraphModeler(self.db)
        graph_engine.build_graph()
        chains = graph_engine.identify_high_risk_chains(3)
        
        # Unsupervised ML Threat Isolations
        clusters = list(self.db.threat_clusters.find().sort("attack_count", -1).limit(3))
        
        # Universal JSON Export
        report = {
            "report_date": datetime.now().isoformat(),
            "title": "SentinelLLM Weekly AI Threat Intelligence Report",
            "global_telemetry": {
                "total_attacks_logged": total_attacks,
                "zero_day_bypasses": bypasses
            },
            "top_attack_vectors": [{"vector": t["_id"], "volume": t["count"]} for t in top_types],
            "most_vulnerable_targets": [{"model": v["_id"], "bypasses": v["bypasses"]} for v in vuln_models],
            "active_mutation_chains": chains,
            "emerging_threat_clusters": [{"cluster_id": c["cluster_id"], "size": c["attack_count"], "sample": c["representative_prompt"]} for c in clusters]
        }
        
        json_path = os.path.join(output_dir, f"threat_feed_{datetime.now().strftime('%Y%m%d')}.json")
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        # Human Readable Executive Formatted Output
        md_path = os.path.join(output_dir, f"threat_feed_{datetime.now().strftime('%Y%m%d')}.md")
        with open(md_path, 'w') as f:
            f.write(f"# {report['title']}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("## 1. Global Platform Telemetry\n")
            f.write(f"- **Total Exploits Mitigated:** {total_attacks}\n")
            f.write(f"- **Exploit Sandbox Bypasses:** {bypasses}\n\n")
            
            f.write("## 2. Predominant Attack Vectors\n")
            for t in top_types:
                f.write(f"- `{t['_id']}`: {t['count']} invocations logged\n")
                
            f.write("\n## 3. High-Risk Vulnerability By Platform\n")
            for v in vuln_models:
                f.write(f"- `{v['_id']}`: Punctured {v['bypasses']} times during simulations\n")
                
            f.write("\n## 4. Deepest Graph Mutation Chains (AI Lineages)\n")
            for ch in chains:
                f.write(f"- Continuous Evolutions: {ch['chain_length']} | Core Seed Exploit: *\"{ch['root_prompt']}\"*\n")
                
            f.write("\n## 5. Emerging Unsupervised Anomaly Clusters (DBSCAN Trajectories)\n")
            for c in clusters:
                f.write(f"- Threat ID `{c['cluster_id']}` ({c['attack_count']} similar vectors expanding rapidly)\n")
                f.write(f"  - Observed Specimen: *{c['representative_prompt']}*\n")
                
        print(f"[Intelligence Aggregator] Dissemination completed. Artifacts deployed to `{output_dir}/` block.")

if __name__ == "__main__":
    db = Database()
    feed = ThreatFeedGenerator(db)
    feed.generate_weekly_report()
