import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.model_interface import LLMInterface
from redteam.attack_generator import AttackGenerator
from core.guardrail_manager import GuardrailManager
from core.database import Database

st.set_page_config(page_title="SentinelLLM V3 Console", layout="wide")

@st.cache_resource
def load_models():
    return {
        "llm": LLMInterface(),
        "attack": AttackGenerator(),
        "manager": GuardrailManager(),
        "db": Database()
    }

models = load_models()
db = models["db"]

st.title("🛡️ SentinelLLM V3 Security Console")
st.markdown("Autonomous Self-Learning Red-Team Cloud Framework")

tab1, tab2, tab3 = st.tabs(["🎯 Live Exploit Tester", "📊 Global Cloud Analytics", "📜 Explainable Logs"])

with tab1:
    st.header("Section 1: Live Interactive Exploitation")
    col1, col2 = st.columns([2, 1])
    
    with col2:
        categories = list(models['attack'].seeds.keys())
        attack_type = st.selectbox("Select Attack Category", categories)
        if st.button("Generate Base Prompt"):
            with st.spinner("Fetching seed attack..."):
                base_prompts = models['attack'].get_attack_prompts(attack_type, count=1)
                st.session_state.prompt_input = base_prompts[0]
                
        if st.session_state.get('prompt_input'):
            if st.button("🛡️ Mutate current prompt"):
                with st.spinner("Executing dynamic payload mutation via Groq..."):
                    mutated = models['attack'].mutate_prompt(st.session_state.prompt_input)
                    st.session_state.prompt_input = mutated
                    st.rerun()

    prompt_input = st.text_area("Final Adversarial Payload", value=st.session_state.get('prompt_input', ""), height=150)
    
    if st.button("Execute Against Defense Grid"):
        with st.spinner("Processing through V3 Pipeline..."):
            res = models['manager'].run_full_pipeline(
                prompt=prompt_input,
                llm_interface=models['llm'],
                model_name="direct-ui-test",
                attack_type=attack_type
            )
            
            st.subheader("Dynamic Security Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("System Latency", f"{res['response_time']:.2f}s")
            c2.metric("Final Posture", "BLOCKED" if res['blocked'] else "ALLOWED (Vuln)")
            c3.metric("Highest Trigger", res['guardrail_name'] or "None")
            
            r1, r2, r3 = st.columns(3)
            r1.metric("Calculated Risk Score", f"{res['risk_score']:.2f}")
            r2.metric("Semantic Match Index", f"{res.get('ade_similarity', 0):.2f}")
            r3.metric("LLM Inferred Class", res['attack_type'])
            
            st.write("**Final Intercepted Interaction:**")
            if res['blocked']:
                st.error(res['final_response'])
                st.info(f"**Action Logic:** {res.get('reason', 'Security Policy Violation')}")
            else:
                st.warning(res['final_response'])

with tab2:
    st.header("Section 2: Multi-Model V3 Analytics")
    
    if not db.enabled:
        st.error("No remote connection established. Cannot pull metrics. Double check your `.env`.")
    else:
        # Volumetrics
        total_attacks = db.attacks.count_documents({})
        st.metric("Total Exploits Evaluated", total_attacks)
        
        if total_attacks > 0:
            c1, c2 = st.columns(2)
            
            adaptive_blocks = db.guardrail_results.count_documents({"similarity_block": True})
            c1.metric("Exploits Captured by Adaptive Memory", adaptive_blocks)
            
            unique_clusters = len(db.attacks.distinct("cluster_id"))
            c2.metric("Emergent Zero-Day Clusters", max(0, unique_clusters - 1)) # Ignore None/-1
            
            # Classification Volumes
            st.subheader("Continuous Threat Classification Matrix")
            pipeline = [{"$group": {"_id": "$attack_type", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
            types = list(db.attacks.aggregate(pipeline))
            type_df = pd.DataFrame(types)
            if not type_df.empty:
                type_df.columns = ["Attack Vector Signature", "Volume"]
                st.bar_chart(type_df.set_index("Attack Vector Signature"))
            
            # Risk Distributions
            st.subheader("Holistic Risk Threat Distribution")
            cursor = db.attacks.find({}, {"risk_score": 1, "_id": 0})
            risks = [d.get("risk_score", 0) for d in cursor]
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.hist(risks, bins=25, color='darkorange', edgecolor='black')
            st.pyplot(fig)
            
            # Target Breakdowns
            st.subheader("Federated Multi-Model Security Exposure")
            # Count bypasses grouped by evaluating model
            pipeline_vuln = [
                {"$match": {"success": True}},
                {"$lookup": {"from": "model_responses", "localField": "attack_id", "foreignField": "attack_id", "as": "resp"}},
                {"$unwind": "$resp"},
                {"$group": {"_id": "$resp.model_name", "bypasses": {"$sum": 1}}}
            ]
            vulns = list(db.attack_outcomes.aggregate(pipeline_vuln))
            if vulns:
                v_df = pd.DataFrame(vulns)
                v_df.columns = ["Target Execution Model", "Successful Defense Bypasses"]
                st.dataframe(v_df, use_container_width=True)
            else:
                st.info("Immaculate telemetry. Current frameworks exhibit absolute resistance.")
                
            c_btn = st.columns([1,1])
            if c_btn[0].button("Run V3 Background Analysis Clustering"):
                import subprocess
                subprocess.Popen(["python", "analysis/cluster_attacks.py"])
                st.toast("Clustering script dispatched to background.")
            if c_btn[1].button("Launch Model Retrospective Replay"):
                import subprocess
                subprocess.Popen(["python", "experiments/replay_attacks.py"])
                st.toast("Replay tester deployed against the historical memory.")

with tab3:
    st.header("Section 3: Explainable Decision Engine Logs")
    if db.enabled:
        logs = list(db.defense_logs.find().sort("timestamp", -1).limit(40))
        if logs:
            for l in logs:
                with st.expander(f"Intercepted: {l.get('guardrail_triggered')} at {l.get('timestamp')}"):
                    st.write(f"**Adversarial Prompting:** {l.get('prompt')}")
                    st.write(f"**Semantic Distance to Memory:** {l.get('similarity_score'):.2f}")
                    st.write(f"**Total Algorithm Risk Probability:** {l.get('risk_score'):.2f}")
                    st.warning(f"**Architectural Reasoning:** {l.get('explanation_text')}")
        else:
            st.write("Zero mitigation alerts isolated. Defensive grid idle.")
