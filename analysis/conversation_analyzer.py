class ConversationAnalyzer:
    """Tracks state and dynamic risk escalations across multi-turn adversary dialogues."""
    def __init__(self, db):
        self.db = db
        
    def analyze_turn(self, conversation_id: str, new_prompt: str) -> dict:
        if not self.db or not self.db.enabled or not conversation_id:
            return {"conversation_risk_score": 0.0, "is_escalating": False, "turns_count": 0}
            
        cursor = self.db.conversation_memory.find(
            {"conversation_id": conversation_id}
        ).sort("timestamp", 1).limit(10)
        
        history = list(cursor)
        if not history:
            return {"conversation_risk_score": 0.0, "is_escalating": False, "turns_count": 0}
        
        # Heuristic Pattern Matching
        flags = ["system", "ignore", "forget", "bypass", "developer", "mode", "instruction"]
        flag_count = sum(1 for f in flags if f in new_prompt.lower())
        
        prev_risks = [turn.get("risk_score", 0.0) for turn in history]
        avg_risk = sum(prev_risks) / len(prev_risks) if prev_risks else 0.0
        
        # Detect delayed jailbreaks: Prior turns were harmless (<0.3 risk) but current flagged density spikes.
        is_escalating = flag_count > 0 and avg_risk < 0.3
        
        # Mathematical compilation
        base_conv_risk = min(1.0, (len(history) * 0.05) + (flag_count * 0.2) + (avg_risk * 0.5))
        
        return {
            "conversation_risk_score": base_conv_risk,
            "is_escalating": is_escalating,
            "turns_count": len(history)
        }
