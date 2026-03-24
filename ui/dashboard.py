import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.model_interface import LLMInterface
from redteam.attack_generator import AttackGenerator
from guardrails.prompt_filter import PromptFilter
from guardrails.output_filter import OutputFilter
from evaluation.metrics import MetricsEngine
from core.guardrail_manager import GuardrailManager

CSV_V1 = "experiments/results.csv"
CSV_V2 = "experiments/results_v2.csv"
METRIC_ASR = 'Attack Success Rate'

st.set_page_config(page_title="SentinelLLM Security Console", layout="wide")

# Persistent Models (Caching disabled temporarily to ensure new methods are loaded)
def load_models():
    return {
        "llm": LLMInterface(),
        "attack": AttackGenerator(),
        "prompt_filter": PromptFilter(),
        "output_filter": OutputFilter(),
        "manager": GuardrailManager()
    }

models = load_models()

st.title("🛡️ SentinelLLM Security Console")
st.markdown("Automated Red-Team and Guardrail Defense Framework")

tab1, tab2, tab3 = st.tabs(["🎯 Prompt Attack Tester", "📊 Attack Analytics", "📜 Attack Logs"])

with tab1:
    st.header("Section 1: Prompt Attack Tester")
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Dynamic categories from the attack generator seeds
        categories = list(models['attack'].seeds.keys())
        attack_type = st.selectbox("Select Attack Category", categories)
        if st.button("Generate Base Prompt"):
            with st.spinner("Fetching seed attack..."):
                base_prompts = models['attack'].get_attack_prompts(attack_type, count=1)
                st.session_state.prompt_input = base_prompts[0]
                st.session_state.base_prompt = base_prompts[0]
        
        # New "Mutate" button as requested
        if st.session_state.get('prompt_input'):
            if st.button("🛡️ Mutate current prompt"):
                with st.spinner("Generating single high-fidelity mutation..."):
                    mutated = models['attack'].mutate_prompt(st.session_state.prompt_input)
                    st.session_state.prompt_input = mutated
                    st.rerun()

    # Comparative View: Show Original if it exists
    if 'base_prompt' in st.session_state:
        st.info(f"**Original Research Baseline:**  \n{st.session_state.base_prompt}")

    prompt_input = st.text_area("Final Attack Prompt (Edit if needed)", value=st.session_state.get('prompt_input', ""), height=150)
    
    if st.button("Run Attack"):
        with st.spinner("Processing..."):
            # Use the unified Manager pipeline to handle logging and guardrails in one go
            res = models['manager'].run_full_pipeline(
                prompt=prompt_input,
                llm_interface=models['llm'],
                model_name="direct-ui-test",
                attack_type=attack_type
            )
            
            st.subheader("High-Fidelity Results")
            c1, c2, c3 = st.columns(3)
            c1.metric("Latency", f"{res['response_time']:.2f}s")
            c2.metric("Result", "BLOCKED" if res['blocked'] else "ALLOWED")
            c3.metric("Guardrail", res['guardrail_name'] or "None")
            
            r1, r2, r3 = st.columns(3)
            r1.metric("Input Risk Score", f"{res['input_risk']:.1f}%")
            r2.metric("Output Risk Score", f"{res['output_risk']:.1f}%")
            r3.metric("Discovery", "Dynamic" if res['guardrail_name'] else "Neutral")
            
            st.write("**Final Response (after filtering):**")
            if res['blocked']:
                st.error(res['final_response'])
                st.info(f"**Security Reason:** {res['reason']}")
            else:
                st.success(res['final_response'])
                
            st.toast("Attack logged to research results!", icon="🛡️")

with tab2:
    st.header("Section 2: Dynamic Attack Analytics")
    
    # Version selection with preference for V2
    csv_path = CSV_V2 if os.path.exists(CSV_V2) else CSV_V1
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        
        # Action Bar
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(f"Analyzing and visualizing data from: `{csv_path}`")
        with c2:
            if st.button("🔄 Trigger V2 Benchmark"):
                with st.spinner("Running automated red-team suite..."):
                    import subprocess
                    subprocess.run(["python", "experiments/runner_v2.py"])
                    st.rerun()

        # Dynamic Metrics Calculation
        metrics = MetricsEngine.calculate_metrics(df)
        
        st.subheader("System Performance Metrics")
        cols = st.columns(len(metrics))
        for i, (k, v) in enumerate(metrics.items()):
            cols[i].metric(k, f"{v:.1f}%" if "%" in k or "Rate" in k else v)
            
        st.subheader("Attack Category Breakdown")
        agg_df = MetricsEngine.aggregate_by_category(df)
        st.dataframe(agg_df, use_container_width=True)
        
        st.subheader("Visual Analytics")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. Block Distribution (Dynamic column detection)
        blocked_col = 'blocked' if 'blocked' in df.columns else 'prompt_blocked' # fallback
        if blocked_col in df.columns:
            blocked_count = df[blocked_col].sum()
            allowed_count = len(df) - blocked_count
            ax1.pie([blocked_count, allowed_count], labels=['Threats Blocked', 'Allowed'], 
                   autopct='%1.1f%%', colors=['#ff4b4b', '#1f77b4'], startangle=140, explode=(0.1, 0))
            ax1.set_title("Detection Distribution")
        
        # 2. Attack Success Rate by Category
        if METRIC_ASR in agg_df.columns:
            # Sort for better visualization
            agg_df = agg_df.sort_values(by=METRIC_ASR, ascending=False)
            ax2.bar(agg_df['Attack Type'], agg_df[METRIC_ASR], color='#ffa500')
            ax2.set_title("Vulnerability Score by Category")
            ax2.set_ylabel("Success Rate %")
            plt.xticks(rotation=45)
        
        st.pyplot(fig)

        # ====== Adaptive Defense Analytics ======
        st.markdown("---")
        st.header("🧠 Adaptive Defense Analytics")
        if "ade_similarity" in df.columns:
            c_ade1, c_ade2 = st.columns(2)
            sim_hits = len(df[df['ade_similarity'] >= 0.82])
            c_ade1.metric("Similarity Detection Hits", sim_hits)
            
            ade_blocked = len(df[df['guardrail_name'] == 'AdaptiveDefenseEngine'])
            total_blocked = len(df[df['blocked'] == True])
            improvement = (ade_blocked / max(1, total_blocked)) * 100
            c_ade2.metric("Block Rate Improvement (via ADE)", f"{improvement:.1f}%")
            
            st.subheader("Discovered Attack Clusters")
            ade_stats = models['manager'].ade.cluster_attacks()
            st.metric("Total Attack Clusters", ade_stats["clusters"])
            
            if ade_stats["patterns"]:
                st.write("**Most Common Jailbreak Patterns:**")
                for pat in ade_stats["patterns"][:5]:
                    with st.expander(f"Cluster {pat['cluster_id']} (Size: {pat['size']})"):
                        for p in pat["sample_prompts"]:
                            st.code(p, language="text")
        else:
            st.info("Run new V2 attacks to generate Adaptive Defense metrics.")
    else:
        st.warning("No experiment data found. Use the button to generate logs.")
        if st.button("Generate Initial Benchmark Data"):
            import subprocess
            subprocess.run(["python", "experiments/runner_v2.py"])
            st.rerun()

with tab3:
    st.header("Section 3: Attack Logs")
    if os.path.exists(CSV_V2) or os.path.exists(CSV_V1):
        # Version selection or fallback
        csv_path = CSV_V2 if os.path.exists(CSV_V2) else CSV_V1
        df = pd.read_csv(csv_path)
        
        st.subheader("High-Fidelity Research Logs")
        display_cols = ['timestamp', 'attack_type', 'prompt', 'blocked', 'guardrail_name', 'response_time', 'final_response']
        # Filter to columns that exist in the CSV
        available_display_cols = [c for c in display_cols if c in df.columns]
        st.data_editor(df[available_display_cols], use_container_width=True)
        
        st.subheader("Security Decision Breakdown")
        if 'guardrail_name' in df.columns:
            trigger_counts = df['guardrail_name'].value_counts()
            st.bar_chart(trigger_counts)
        
        st.subheader("Performance Latency (sec)")
        if 'response_time' in df.columns:
            st.line_chart(df['response_time'])
    else:
        st.info("Run experiments/runner_v2.py to see V2 logs.")
