"use client";
import React from "react";
import { motion } from "framer-motion";
import { Shield, Zap, Target, Database, Activity, Cpu, ArrowRight, Layout, Users, Lock } from "lucide-react";
import { GlassCard, NeonButton } from "../components/ui-elements";

export default function Home() {
  return (
    <div className="relative min-h-screen w-full bg-[#020617] text-white">
      {/* Background Glows */}
      <div className="fixed -left-[10%] -top-[10%] h-[500px] w-[500px] rounded-full bg-indigo-600/20 blur-[120px]" />
      <div className="fixed -right-[10%] bottom-[10%] h-[500px] w-[500px] rounded-full bg-violet-600/20 blur-[120px]" />

      {/* Navigation */}
      <nav className="fixed top-0 z-50 flex w-full items-center justify-between border-b border-white/5 bg-black/20 px-8 py-4 backdrop-blur-lg">
        <div className="flex items-center gap-2">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">AEGIS</span>
        </div>
        <div className="hidden gap-8 text-sm font-medium text-gray-400 md:flex">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="/dashboard" className="hover:text-white transition-colors">Dashboard</a>
          <a href="#security" className="hover:text-white transition-colors">Security</a>
        </div>
        <div className="flex items-center gap-4">
          <NeonButton variant="secondary" className="px-4 py-2">Log In</NeonButton>
          <NeonButton className="px-5 py-2">Get Started</NeonButton>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center px-4 pt-32 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-400"
        >
          <Zap className="h-4 w-4" />
          <span>V5 Evolution Intelligence Active</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="mb-8 max-w-4xl text-6xl font-extrabold tracking-tight md:text-8xl"
        >
          Secure the Intelligence, <br />
          <span className="gradient-text">AEGIS Autonomous Security</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-12 max-w-2xl text-lg text-gray-400 md:text-xl"
        >
          Professional-grade AI security framework engineered to stress-test, analyze, and reinforce the safety boundaries of Large Language Models through adaptive red-teaming.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="flex flex-wrap justify-center gap-6"
        >
          <a href="/dashboard">
            <NeonButton className="h-14 px-10 text-lg">
              Launch Dashboard <ArrowRight className="h-5 w-5 ml-2" />
            </NeonButton>
          </a>
          <NeonButton variant="secondary" className="h-14 px-10 text-lg">
            View Analytics
          </NeonButton>
        </motion.div>
      </section>

      {/* Core Features Grid */}
      <section id="features" className="mx-auto max-w-7xl px-8 py-24">
        <div className="mb-16 text-center">
            <h2 className="text-4xl font-bold">Key Capabilities</h2>
            <p className="mt-4 text-gray-400">Military-grade protection for your neural architectures.</p>
        </div>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          <GlassCard delay={0.1}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500/20 text-indigo-500">
              <Zap className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Autonomous Red-Teaming</h3>
            <p className="text-sm text-gray-400">AI-driven generation of complex adversarial prompts to identify vulnerabilities before they emerge.</p>
          </GlassCard>

          <GlassCard delay={0.2}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-500/20 text-violet-500">
              <Target className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Neural Payload Mutation</h3>
            <p className="text-sm text-gray-400">V5 mutation logic that abstracts and evolves attack vectors using semantic memory feedback loops.</p>
          </GlassCard>

          <GlassCard delay={0.3}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-500/20 text-cyan-500">
              <Shield className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Multi-Layered Guardrails</h3>
            <p className="text-sm text-gray-400">Seamless integration of Rebuff, Presidio, NeMo, and LlamaFirewall middleware pipelines.</p>
          </GlassCard>

          <GlassCard delay={0.4}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-pink-500/20 text-pink-500">
              <Database className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Threat Archives</h3>
            <p className="text-sm text-gray-400">High-fidelity telemetry storage with behavioral risk scoring and automated executive reporting.</p>
          </GlassCard>

          <GlassCard delay={0.5}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-500">
              <Activity className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Live Monitoring</h3>
            <p className="text-sm text-gray-400">Real-time system execution response tracking and thread saturation metrics under heavy load.</p>
          </GlassCard>

          <GlassCard delay={0.6}>
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-orange-500/20 text-orange-500">
              <Cpu className="h-8 w-8" />
            </div>
            <h3 className="mb-2 text-xl font-bold">Model Benchmarking</h3>
            <p className="text-sm text-gray-400">Comparative resiliency evaluation across Gemini, LLaMA, and internal NLP engines.</p>
          </GlassCard>
        </div>
      </section>

      {/* Trust / Creator Section */}
      <section className="border-t border-white/5 bg-white/5 py-24 backdrop-blur-sm">
        <div className="mx-auto max-w-4xl px-8 text-center">
          <div className="mb-8 flex justify-center">
            <Lock className="h-16 w-16 text-indigo-500 opacity-50" />
          </div>
          <h2 className="mb-6 text-4xl font-bold">Engineered for Security</h2>
          <p className="mb-12 text-lg text-gray-400 leading-relaxed italic">
             "As Large Language Models move into core business infrastructure, they introduce non-deterministic vulnerabilities that legacy protocols cannot defend against."
          </p>
          <div className="flex flex-col items-center">
            <span className="font-bold text-xl">THRIVIKRAM G</span>
            <span className="text-indigo-400 text-sm tracking-widest uppercase mt-1">Chief Architect & Security Researcher</span>
            <div className="mt-6 flex gap-4">
              <a href="https://linkedin.com/in/thrivikramg" target="_blank" className="hover:text-indigo-500 transition-colors">
                <Users className="h-6 w-6" />
              </a>
              <a href="#" className="hover:text-indigo-500 transition-colors">
                <Layout className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 px-8 pt-20 pb-10 text-center text-sm text-gray-500">
        <p>© 2026 AEGIS AI Security. All rights reserved.</p>
      </footer>
    </div>
  );
}
