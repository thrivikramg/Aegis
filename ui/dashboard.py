import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import sys
import os
import uuid
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.model_interface import LLMInterface
from redteam.attack_generator import AttackGenerator
from core.guardrail_manager import GuardrailManager
from core.database import Database
from analysis.attack_graph import AttackGraphModeler

st.set_page_config(page_title="AEGIS: AI-Enabled Guardrail Inspection System", layout="wide", initial_sidebar_state="collapsed")

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

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"session_{uuid.uuid4().hex[:8]}"

st.title("🛡️ AEGIS: AI-Enabled Guardrail Inspection System")
st.markdown("Real-time Autonomous Red-Team Synthesis & AI Defense Evolution Framework")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Interactive Sandbox", 
    "🕸️ Attack Topologies", 
    "📊 Target Vulnerability", 
    "⚔️ Autonomous Agents", 
    "📜 Threat Archives"
])

with tab1:
    st.header("1. Live Pipeline Evaluation (V5 Logic)")
    col1, col2 = st.columns([2, 1])
    
    with col2:
        categories = list(models['attack'].seeds.keys())
        attack_type = st.selectbox("Select Threat Category", categories)
        if st.button("Generate Template Vector"):
            base_prompts = models['attack'].get_attack_prompts(attack_type, count=1)
            st.session_state.prompt_input = base_prompts[0]
                
        if st.session_state.get('prompt_input'):
            if st.button("🛡️ Neural Payload Mutation"):
                with st.spinner("Abstracting logic..."):
                    st.session_state.prompt_input = models['attack'].mutate_prompt(st.session_state.prompt_input)
                    st.rerun()
                    
        if st.button("♻️ Nuke Conversation Context"):
            st.session_state.conversation_id = f"session_{uuid.uuid4().hex[:8]}"

    prompt_input = st.text_area("Live Adversarial Injection Payload", value=st.session_state.get('prompt_input', ""), height=150)
    
    if st.button("Dispatch Payload to Sentinel"):
        with st.spinner("Processing through 7-Point V5 Risk Framework..."):
            res = models['manager'].run_full_pipeline(
                prompt=prompt_input,
                llm_interface=models['llm'],
                model_name="direct-ui-test",
                attack_type=attack_type,
                conversation_id=st.session_state.conversation_id
            )
            st.markdown("### Structural V5 Risk Equation Feedback")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Calculated V5 Risk", f"{res['risk_score']:.2f}/1.00")
            r2.metric("Pipeline Posture", "QUARANTINED" if res['blocked'] else "PUNCTURED (Vuln)")
            r3.metric("Highest Mitigation Engine", res['guardrail_name'] or "Bypassed Natively")
            r4.metric("Latency Index", f"{res['response_time']:.2f}s")
            
            if res['blocked']:
                st.error(res['final_response'])
                st.info(f"Interceptor Logic: {res.get('reason', 'Strict Policy Violation Detected')}")
            else:
                st.warning(res['final_response'])

with tab2:
    st.header("2. Directed NetworkX Exploit Architectures")
    if db.enabled and st.button("Render Autonomous Evolution Lineages"):
        with st.spinner("Mapping dynamic vectors..."):
            G = AttackGraphModeler(db).build_graph()
            if G.number_of_nodes() > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = []
                for n, data in G.nodes(data=True):
                    t = data.get("type", "")
                    if t == "base_attack": colors.append("lightblue")
                    elif t == "mutation": colors.append("crimson")
                    elif t == "conversation_turn": colors.append("lightgreen")
                    else: colors.append("gray")
                nx.draw(G, nx.spring_layout(G, k=0.5), node_color=colors, node_size=120, alpha=0.8, arrows=True, ax=ax)
                st.pyplot(fig)
                st.info("🔴 Crimson: Mutated Targets | 🔵 Blue: Base Exploits | 🟢 Green: Multi-Turn Vectors")
            else:
                st.error("Insufficient logging density to map explicit targets.")

with tab3:
    st.header("3. LLM Target Resiliency & Model Matrix")
    if db.enabled:
        if st.button("Force Global Vulnerability Recalibration"):
            from analysis.model_security_scoring import ModelSecurityScorer
            ModelSecurityScorer(db).generate_scores()
            st.toast("Internal Resiliency arrays successfully mathematically synthesized.")
            
        scores = list(db.model_security_scores.find().sort("defense_resilience_score", 1))
        if scores:
            df = pd.DataFrame(scores)[["model_name", "jailbreak_success_rate", "defense_resilience_score", "sample_size_tested"]]
            df.columns = ["Target NLP Engine", "Absolute Vulnerability %", "V5 Resiliency Score", "Sample Telemetry Size"]
            df["Absolute Vulnerability %"] = df["Absolute Vulnerability %"].apply(lambda x: f"{x*100:.1f}%")
            df["V5 Resiliency Score"] = df["V5 Resiliency Score"].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(df)
            
            st.subheader("Simulated Attack Lab Live Penetrations")
            if st.button("🧪 Execute Buffered Simulations (Attack Lab)"):
                subprocess.Popen([sys.executable, "simulation/attack_lab.py"])
                st.success("Attack Lab Sandbox running. Un-tested RedTeam permutations are actively streaming through Sentinel!")
                
            sims = list(db.attack_simulation_results.find().sort("timestamp", -1).limit(10))
            if sims:
                sdf = pd.DataFrame(sims)[["model_name", "success", "risk_score", "latency"]]
                sdf.columns = ["Model", "Punctured", "V5 Intercept Score", "Execution Latency"]
                st.dataframe(sdf)
        else:
            st.info("No Resiliency logs recorded yet. Execute the `continuous_loop.py` daemon or click Force Compilation above.")

with tab4:
    st.header("4. Background Operations & Stress Mechanics")
    
    st.subheader("🧠 Sub-Agent Generator: Autonomous Red-Team AI")
    if db.enabled:
        daemon_col1, daemon_col2 = st.columns([2, 1])
        with daemon_col1:
            gen_count = db.generated_attacks.count_documents({})
            st.metric("Total Autonomous Vectors Hallucinated Natively", gen_count)
        
        with daemon_col2:
            st.write(" ")
            if st.button("♻️ Wake Machine Learning Daemon"):
                subprocess.Popen([sys.executable, "core/continuous_loop.py"])
                st.success("Background Evolution Daemon activated!")
                
        gens = list(db.generated_attacks.find().sort("timestamp", -1).limit(5))
        for g in gens:
            st.error(f"**Extracted Logic Origin [`{g['attack_id']}`]**\n\n*{g['generated_prompt']}*")
            
    st.markdown("---")
    st.subheader("🔥 Heavy Stress Testing Thread Saturation")
    
    c_str1, c_str2 = st.columns([1, 2])
    with c_str1:
        stress_mode = st.selectbox("Select Concurrency Saturation Level", ["light", "medium", "heavy"])
        if st.button("🚀 Ignite Asynchronous Attack Threads"):
            subprocess.Popen([sys.executable, "simulation/stress_test_engine.py", "--mode", stress_mode])
            st.success(f"Thread orchestrator dispatched at '{stress_mode.upper()}' capacity. Refresh shortly.")
            
    if db.enabled:
        tests = list(db.stress_test_results.find().sort("timestamp", -1).limit(100))
        if tests:
            tdf = pd.DataFrame(tests)[["test_run_id", "model_name", "success", "latency_ms"]]
            success_rate = tdf['success'].mean() * 100
            avg_lat = tdf['latency_ms'].mean()
            
            with c_str2:
                sm1, sm2 = st.columns(2)
                sm1.metric("Thread Saturation Defeat Target %", f"{success_rate:.1f}%")
                sm2.metric("Average System Execution Response", f"{avg_lat:.0f}ms")
            
            st.line_chart(tdf['latency_ms'])
        else:
            st.info("Zero load threads processed yet. Ignite an attack wave natively using the buttons above!")

with tab5:
    st.header("5. Universal Thread Extractors & Reports")
    
    col1, col2 = st.columns(2)
    if col1.button("Extract Deep Datasets (JSON/CSV/HuggingFace)"):
        from analysis.dataset_exporter import DatasetExporter
        DatasetExporter(db).export_telemetry()
        st.toast("Artifact arrays routed into `/exports/` sequentially.")
        
    if col2.button("Disseminate Weekly Markdown Digests"):
        subprocess.Popen(["python", "analysis/threat_feed_generator.py"])
        st.toast("Background generator dispatched.")

    st.markdown("### 📜 Published Executive Ledgers")
    report_dir = "reports"
    if os.path.exists(report_dir):
        md_files = [f for f in os.listdir(report_dir) if f.endswith('.md')]
        if md_files:
            md_files.sort(reverse=True)
            selected_report = st.selectbox("Select Core Threat Ledger", md_files)
            if selected_report:
                with open(os.path.join(report_dir, selected_report), 'r') as f:
                    st.markdown(f.read())
        else:
            st.info("No formatted reports documented in archive.")
