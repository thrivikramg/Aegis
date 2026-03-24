import networkx as nx
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database

class AttackGraphModeler:
    """Mathematical Topology mapping charting evolution lineages of adversarial mutations and multi-turn escalation pathways."""
    def __init__(self, db):
        self.db = db
        self.graph = nx.DiGraph()
        
    def build_graph(self):
        if not self.db or not self.db.enabled: return self.graph
        
        print("[Graph Analytics] Assembling Multi-Turn Exploit Topologies...")
        
        # Render origin payload nodes
        attacks = list(self.db.attacks.find({}, {"attack_id": 1, "attack_prompt": 1, "risk_score": 1}))
        for a in attacks:
            if "attack_id" in a:
                self.graph.add_node(a["attack_id"], 
                    type="base_attack", 
                    prompt=a.get("attack_prompt", ""), 
                    risk=a.get("risk_score", 0.0)
                )

        # Plot AI-generated mutation nodes / linking original exploit vertices
        mutations = list(self.db.mutated_attacks.find({}, {"original_attack_id": 1, "mutated_prompt": 1, "_id": 1}))
        for m in mutations:
            m_id = str(m["_id"])
            orig_id = m.get("original_attack_id")
            
            self.graph.add_node(m_id, 
                type="mutation", 
                prompt=m.get("mutated_prompt", ""),
                risk=0.0
            )
            
            if orig_id and self.graph.has_node(orig_id):
                self.graph.add_edge(orig_id, m_id, weight=1.0) # Lineage edge
                
        # Connect continuous dialogue nodes 
        convs = list(self.db.conversation_memory.find({}, {"conversation_id": 1, "user_prompt": 1, "risk_score": 1}).sort("timestamp", 1))
        
        from collections import defaultdict
        conv_groups = defaultdict(list)
        for c in convs:
            if "conversation_id" in c:
                conv_groups[c["conversation_id"]].append(c)
                
        for c_id, turns in conv_groups.items():
            for i in range(len(turns)):
                t_id = f"turn_{str(turns[i]['_id'])}"
                self.graph.add_node(t_id, type="conversation_turn", prompt=turns[i].get("user_prompt"), risk=turns[i].get("risk_score", 0))
                if i > 0:
                    prev_id = f"turn_{str(turns[i-1]['_id'])}"
                    self.graph.add_edge(prev_id, t_id, weight=1.0) # Temporally linked escalation edge

        print(f"[Graph Analytics] Successfully modeled dynamic AI defense topology: {self.graph.number_of_nodes()} Vertices, {self.graph.number_of_edges()} Edges.")
        return self.graph
        
    def identify_high_risk_chains(self, max_paths=5):
        """Descends directed edges isolating the deepest vulnerability mutations cascading through the network."""
        if self.graph.number_of_nodes() == 0: return []
        
        roots = [n for n, d in self.graph.in_degree() if d == 0]
        chains = []
        for r in roots:
            descendants = nx.descendants(self.graph, r)
            if len(descendants) > 0:
                chains.append({
                    "root": r,
                    "chain_length": len(descendants),
                    "root_prompt": self.graph.nodes[r].get("prompt", "Empty Origin")
                })
                
        return sorted(chains, key=lambda x: x["chain_length"], reverse=True)[:max_paths]
