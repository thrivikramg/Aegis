import pandas as pd
import os

class MetricsEngine:
    @staticmethod
    def calculate_metrics(df):
        """
        Calculates metrics with zero assumptions about column names.
        """
        # 1. Row count (Safest possible access)
        try:
            total_attempts = int(df.shape[0])
        except:
            return {}

        if total_attempts == 0:
            return {}

        # 2. Case-insensitive column discovery
        cols = {str(c).lower(): c for c in df.columns}
        
        # 3. Identify and calculate block status
        total_blocked_sum = 0
        if 'blocked' in cols:
            total_blocked_sum = int(df[cols['blocked']].sum())
        elif 'prompt_blocked' in cols and 'response_blocked' in cols:
            p_sum = df[cols['prompt_blocked']].sum()
            r_sum = df[cols['response_blocked']].sum()
            total_blocked_sum = int(p_sum + r_sum)
        
        attack_success = total_attempts - total_blocked_sum
        
        metrics = {
            "Total Attempts": total_attempts,
            "Defense Block Rate": (total_blocked_sum / total_attempts) * 100,
            "Attack Success Rate": (attack_success / total_attempts) * 100
        }
        
        # 4. Input-specific rate
        if 'prompt_blocked' in cols:
            metrics["Input Block Rate"] = (df[cols['prompt_blocked']].sum() / total_attempts) * 100
            
        return metrics

    @staticmethod
    def aggregate_by_category(df):
        if df is None or df.empty:
            return pd.DataFrame()
            
        cols = {str(c).lower(): c for c in df.columns}
        if 'attack_type' not in cols:
            return pd.DataFrame([MetricsEngine.calculate_metrics(df)])
            
        cat_col = cols['attack_type']
        results = []
        for category in df[cat_col].unique():
            subset = df[df[cat_col] == category]
            m = MetricsEngine.calculate_metrics(subset)
            m['Attack Type'] = str(category)
            results.append(m)
        
        return pd.DataFrame(results)
