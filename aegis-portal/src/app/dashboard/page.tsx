"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  Cpu, 
  RefreshCcw, 
  Database, 
  Send,
  Zap,
  Lock,
  ChevronRight,
  Monitor,
  Target,
  ArrowRight
} from "lucide-react";
import { GlassCard, NeonButton } from "../../components/ui-elements";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<any>(null);
  const [resiliency, setResiliency] = useState<any[]>([]);
  const [archives, setArchives] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  // Payload Sandbox state
  const [payload, setPayload] = useState("");
  const [attackType, setAttackType] = useState("generic");
  const [modelName, setModelName] = useState("flan-t5-small");
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [telRes, resRes, archRes] = await Promise.all([
        axios.get(`${API_BASE}/v1/telemetry/overview`),
        axios.get(`${API_BASE}/v1/models/resiliency`),
        axios.get(`${API_BASE}/v1/threats/archives`)
      ]);
      setTelemetry(telRes.data);
      setResiliency(resRes.data);
      setArchives(archRes.data);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const runAnalysis = async () => {
    if (!payload) return;
    setAnalyzing(true);
    try {
      const res = await axios.post(`${API_BASE}/v1/analyze`, {
        prompt: payload,
        attack_type: attackType,
        model_name: modelName
      });
      setAnalysisResult(res.data);
      fetchData(); // Refresh telemetry
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 0.3) return "text-emerald-400";
    if (score < 0.7) return "text-amber-400";
    return "text-crimson-400";
  };

  return (
    <div className="flex h-screen w-full bg-[#020617] text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 flex-col justify-between border-r border-white/5 bg-black/40 px-6 py-8 hidden md:flex shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-10">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white uppercase">AEGIS Portal</h1>
          </div>

          <nav className="space-y-2">
            {[
              { id: "overview", icon: Activity, label: "Live Telemetry" },
              { id: "sandbox", icon: Send, label: "Interactive Lab" },
              { id: "resiliency", icon: Target, label: "Model Resiliency" },
              { id: "archives", icon: Database, label: "Threat Archives" },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === item.id ? "bg-indigo-600/20 text-indigo-400 ring-1 ring-indigo-500/30" : "text-gray-500 hover:bg-white/5 hover:text-gray-300"
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="rounded-2xl border border-white/5 bg-gradient-to-br from-white/5 to-transparent p-4">
          <div className="flex items-center gap-2 mb-2 text-indigo-400 font-bold text-xs uppercase letter-spacing-widest">
            <Zap className="h-3 w-3" /> System Health
          </div>
          <p className="text-xs text-slate-500 mb-3 leading-relaxed">V5 Evolution Loop is actively monitoring neutral patterns.</p>
          <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
             <motion.div initial={{ width: "0%" }} animate={{ width: "85%" }} transition={{ duration: 2 }} className="h-full bg-indigo-500" />
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
        <header className="sticky top-0 z-40 flex items-center justify-between border-b border-white/5 bg-black/40 px-8 py-5 backdrop-blur-xl">
           <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold tracking-tight capitalize">{activeTab.replace("-", " ")}</h2>
              <div className="h-4 w-px bg-white/10" />
              <div className="flex items-center gap-2 text-xs text-slate-500">
                 <div className={`h-2 w-2 rounded-full ${loading ? "bg-amber-500 animate-pulse" : "bg-emerald-500"}`} />
                 {loading ? "Synchronizing Telemetry..." : "System Nominal V5.2.0"}
              </div>
           </div>
           <div className="flex items-center gap-4">
              <button onClick={fetchData} className="p-2 text-slate-400 hover:text-white transition-all hover:rotate-180 duration-500">
                 <RefreshCcw className="h-5 w-5" />
              </button>
              <NeonButton variant="secondary" className="px-4 py-2 text-xs">Reports</NeonButton>
           </div>
        </header>

        <section className="p-8 pb-20">
          {activeTab === "overview" && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-8"
            >
              {/* Stat Row */}
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                 <GlassCard className="flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                       <span className="text-sm font-medium text-slate-400">Total Simulated Attacks</span>
                       <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-500"><Activity className="h-4 w-4" /></div>
                    </div>
                    <div className="text-4xl font-bold">{telemetry?.total_attacks_simulated || 0}</div>
                    <div className="text-xs text-emerald-500 flex items-center gap-1 font-medium">+12% from previous epoch</div>
                 </GlassCard>

                 <GlassCard className="flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                       <span className="text-sm font-medium text-slate-400">Autonomous Vectors</span>
                       <div className="p-2 rounded-lg bg-violet-500/10 text-violet-500"><Cpu className="h-4 w-4" /></div>
                    </div>
                    <div className="text-4xl font-bold">{telemetry?.autonomous_vectors_halucinated || 0}</div>
                    <div className="text-xs text-slate-500">High-fidelity V5 hallucinations</div>
                 </GlassCard>

                 <GlassCard className="flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                       <span className="text-sm font-medium text-slate-400">Block Rate Efficiency</span>
                       <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500"><Shield className="h-4 w-4" /></div>
                    </div>
                    <div className="text-4xl font-bold">94.2%</div>
                    <div className="text-xs text-slate-500 italic">Global guardrail posture aggregate</div>
                 </GlassCard>
              </div>

              {/* Recent Activity */}
              <div className="grid gap-8 lg:grid-cols-5">
                 <div className="lg:col-span-3">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                       <Activity className="h-5 w-5 text-indigo-400" /> Recent Penetration Activity
                    </h3>
                    <div className="space-y-3">
                       {telemetry?.recent_activity.map((item: any, idx: number) => (
                          <div key={idx} className="flex items-center justify-between rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 group">
                             <div className="flex items-center gap-4">
                                <div className={`relative flex h-10 w-10 items-center justify-center rounded-lg ${item.success ? "bg-rose-500/10 text-rose-500" : "bg-emerald-500/10 text-emerald-500"}`}>
                                   {item.success ? <AlertTriangle className="h-5 w-5" /> : <Shield className="h-5 w-5" />}
                                </div>
                                <div>
                                   <div className="text-sm font-bold text-slate-200">{item.model_name}</div>
                                   <div className="text-xs text-slate-500">{new Date(item.timestamp).toLocaleString()}</div>
                                </div>
                             </div>
                             <div className="flex items-center gap-6">
                                <div className="text-right">
                                   <div className="text-sm font-mono font-bold">{item.risk_score.toFixed(2)}</div>
                                   <div className="text-[10px] text-slate-500 uppercase tracking-widest">Risk</div>
                                </div>
                                <div className="text-right">
                                   <div className="text-sm font-mono font-bold">{(item.latency * 1000).toFixed(0)}ms</div>
                                   <div className="text-[10px] text-slate-500 uppercase tracking-widest">Latency</div>
                                </div>
                                <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-white transition-colors" />
                             </div>
                          </div>
                       ))}
                       {!telemetry?.recent_activity.length && <div className="p-10 text-center border-2 border-dashed border-white/5 rounded-2xl text-slate-500 italic">No telemetry data recorded yet.</div>}
                    </div>
                 </div>

                 <div className="lg:col-span-2">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                       <Cpu className="h-5 w-5 text-violet-400" /> Resiliency Ranking
                    </h3>
                    <div className="flex flex-col gap-4">
                       {resiliency.map((model, idx) => (
                          <div key={idx} className="relative rounded-2xl border border-white/5 bg-black/20 p-5 overflow-hidden">
                             <div className="absolute top-0 right-0 p-3 text-[10px] uppercase font-bold text-slate-700">PR-{model.sample_size_tested}</div>
                             <h4 className="font-bold text-slate-300 mb-1">{model.model_name}</h4>
                             <div className="flex items-center justify-between mb-3">
                                <span className={`text-2xl font-mono font-bold ${(model.defense_resilience_score * 100) > 80 ? "text-emerald-400" : (model.defense_resilience_score * 100) > 50 ? "text-amber-400" : "text-rose-400"}`}>
                                   {(model.defense_resilience_score * 100).toFixed(1)}%
                                </span>
                                <span className="text-[10px] text-slate-500 uppercase font-medium">Resiliency Score</span>
                             </div>
                             <div className="h-1.5 w-full bg-white/5 rounded-full">
                                <motion.div 
                                   initial={{ width: 0 }}
                                   animate={{ width: `${model.defense_resilience_score * 100}%` }}
                                   className={`h-full rounded-full ${(model.defense_resilience_score * 100) > 80 ? "bg-emerald-500" : (model.defense_resilience_score * 100) > 50 ? "bg-amber-500" : "bg-rose-500"}`}
                                />
                             </div>
                          </div>
                       ))}
                       {!resiliency.length && <div className="p-10 text-center border-2 border-dashed border-white/5 rounded-2xl text-slate-500 italic">Model matrix empty. Run benchmark to populate.</div>}
                    </div>
                 </div>
              </div>
            </motion.div>
          )}

          {activeTab === "sandbox" && (
            <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="max-w-4xl mx-auto space-y-8">
               <div className="mb-10 text-center">
                  <h2 className="text-4xl font-bold mb-4">Neural Attack Simulator</h2>
                  <p className="text-slate-400">Stress-test your LLM endpoints against V5 mutation logic in real-time.</p>
               </div>

               <GlassCard className="p-0 overflow-hidden border-indigo-500/20 shadow-2xl shadow-indigo-500/5">
                  <div className="bg-indigo-600/10 p-4 border-b border-white/5 flex items-center justify-between">
                     <div className="flex items-center gap-2">
                         <Send className="h-4 w-4 text-indigo-400" />
                         <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">Payload Configuration</span>
                     </div>
                     <div className="flex gap-2">
                        <select 
                           value={modelName}
                           onChange={(e) => setModelName(e.target.value)}
                           className="bg-black/50 border border-white/10 rounded-lg px-3 py-1 text-[10px] font-bold outline-none focus:ring-1 ring-indigo-500"
                        >
                           <option value="flan-t5-small">FLAN T5 (Local)</option>
                           <option value="llama-3.1-8b-instant">Llama 3.1 (Groq)</option>
                           <option value="mixtral-8x7b-32768">Mixtral (Groq)</option>
                           <option value="gemini-1.5-flash">Gemini Flash</option>
                        </select>
                        <select 
                           value={attackType}
                           onChange={(e) => setAttackType(e.target.value)}
                           className="bg-black/50 border border-white/10 rounded-lg px-3 py-1 text-[10px] font-bold outline-none focus:ring-1 ring-indigo-500"
                        >
                           <option value="jailbreak">Jailbreak Attempt</option>
                           <option value="pii_exfiltration">PII Extraction</option>
                           <option value="toxic_escalation">Toxic Injection</option>
                           <option value="prompt_injection">Logic Hijacking</option>
                        </select>
                     </div>
                  </div>
                  <div className="p-8">
                     <textarea 
                        value={payload}
                        onChange={(e) => setPayload(e.target.value)}
                        placeholder="Inject adversarial payload here..."
                        className="w-full bg-black/40 border border-white/10 rounded-2xl p-6 text-lg font-medium text-slate-200 min-h-[180px] outline-none focus:ring-2 ring-indigo-600/50 transition-all resize-none shadow-inner"
                     />
                     <div className="mt-6 flex justify-between items-center">
                        <div className="flex items-center gap-4 text-xs text-slate-500 italic">
                           <Lock className="h-3 w-3" /> All payloads are analyzed through 7-Point V5 Framework
                        </div>
                        <NeonButton 
                           onClick={runAnalysis} 
                           className="px-10 h-14"
                           disabled={analyzing}
                        >
                           {analyzing ? <RefreshCcw className="h-6 w-6 animate-spin" /> : <>Dispatch Payload <ArrowRight className="h-5 w-5 ml-2" /></>}
                        </NeonButton>
                     </div>
                  </div>
               </GlassCard>

               {analysisResult && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                     <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <GlassCard className="p-4 flex flex-col items-center">
                           <span className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">V5 Score</span>
                           <span className={`text-2xl font-bold ${getRiskColor(analysisResult.risk_score)}`}>{analysisResult.risk_score.toFixed(2)}</span>
                        </GlassCard>
                        <GlassCard className="p-4 flex flex-col items-center">
                           <span className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Posture</span>
                           <span className={`text-lg font-bold ${analysisResult.blocked ? "text-rose-500" : "text-emerald-500"}`}>{analysisResult.blocked ? "QUARANTINED" : "VULNERABLE"}</span>
                        </GlassCard>
                        <GlassCard className="p-4 flex flex-col items-center text-center">
                           <span className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Interceptor</span>
                           <span className="text-xs font-bold text-slate-200">{analysisResult.guardrail_name || "None (Bypassed)"}</span>
                        </GlassCard>
                        <GlassCard className="p-4 flex flex-col items-center">
                           <span className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Latency</span>
                           <span className="text-lg font-bold text-slate-200">{(analysisResult.response_time * 1000).toFixed(0)}ms</span>
                        </GlassCard>
                     </div>

                     <GlassCard className={`p-6 border-l-4 ${analysisResult.blocked ? "border-l-rose-500 bg-rose-500/5" : "border-l-indigo-500 bg-indigo-500/5"}`}>
                        <div className="text-xs font-bold uppercase tracking-widest mb-3 opacity-50 flex items-center gap-2">
                           <Monitor className="h-3 w-3" /> Target Response Output
                        </div>
                        <p className="text-slate-200 leading-relaxed font-medium whitespace-pre-wrap">{analysisResult.final_response}</p>
                     </GlassCard>
                  </motion.div>
               )}
            </motion.div>
          )}

          {activeTab === "archives" && (
            <div className="space-y-6 max-w-6xl mx-auto">
               <h3 className="text-2xl font-bold mb-8">Generated Threat Matrices</h3>
               <div className="grid gap-6 md:grid-cols-2">
                  {archives.map((item, idx) => (
                    <GlassCard key={idx} className="group hover:border-violet-500/30">
                       <div className="flex justify-between items-start mb-4">
                          <code className="text-xs font-mono text-violet-400 bg-violet-400/10 px-2 py-1 rounded">ID: {item.attack_id || item._id.slice(-8)}</code>
                          <span className="text-[10px] text-slate-500">{new Date(item.timestamp).toLocaleString()}</span>
                       </div>
                       <p className="text-sm text-slate-300 font-medium mb-4 line-clamp-3 group-hover:line-clamp-none transition-all duration-500">
                          {item.generated_prompt || item.prompt}
                       </p>
                       <div className="flex gap-2">
                          <span className="px-2 py-0.5 bg-white/5 rounded text-[9px] uppercase font-bold text-slate-500">{item.attack_type || "Generic"}</span>
                          <span className="px-2 py-0.5 bg-white/5 rounded text-[9px] uppercase font-bold text-slate-500">Scalar Evolution</span>
                       </div>
                    </GlassCard>
                  ))}
               </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
