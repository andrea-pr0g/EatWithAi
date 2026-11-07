import React from 'react';
import { 
  Orbit, 
  Sparkles, 
  Bot, 
  Flame, 
  ShieldCheck, 
  Globe, 
  ArrowRight,
  Cpu
} from 'lucide-react';

export default function ExperienceSection({ onOpenChat }) {
  const features = [
    {
      icon: <Globe className="w-6 h-6 text-cyan-400" />,
      title: "Panoramic Earth Views",
      subtitle: "Elevation 408 km",
      description: "Dine while gazing upon planet Earth through ultra-clear reinforced quartz domes. Experience 16 celestial sunrises every 24 hours.",
      highlight: "Unobstructed Views"
    },
    {
      icon: <Flame className="w-6 h-6 text-violet-400" />,
      title: "Wood-Smoked Gastronomy",
      subtitle: "USDA Prime & Texas BBQ",
      description: "Charcoal-seared Ribeyes and 14-hour post-oak smoked brisket prepared by master pitmasters in our specialized orbital convection kitchens.",
      highlight: "Charbroiled Fresh"
    },
    {
      icon: <Cpu className="w-6 h-6 text-sky-400" />,
      title: "Gemini AI Concierge",
      subtitle: "Smart Table Intelligence",
      description: "Instant table availability, dietary advice, and seamless reservations managed by Google Gemini, accessible via the bottom-right beacon.",
      highlight: "Instant Assistance"
    },
    {
      icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
      title: "Multi-Layer Guardrails",
      subtitle: "Strict Safety Architecture",
      description: "Our AI host features real-time database grounding, prompt injection defenses, and strict booking confirmation barriers for 100% reliability.",
      highlight: "Enterprise Guardrails"
    }
  ];

  return (
    <section id="experience" className="py-24 relative overflow-hidden bg-cosmos-900/60 border-y border-white/5 cosmic-stars">
      {/* Ambient background lighting */}
      <div className="absolute top-1/3 -left-48 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/3 -right-48 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 text-xs font-mono mb-4">
            <Orbit className="w-3.5 h-3.5 text-cyan-400 animate-spin" style={{ animationDuration: '12s' }} />
            <span>THE ORBITAL PLATFORM EXPERIENCE</span>
          </div>
          <h2 className="font-orbitron text-3xl sm:text-5xl font-extrabold text-white tracking-wide">
            An Unprecedented <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400 bg-clip-text text-transparent">Culinary Voyage</span>
          </h2>
          <p className="text-slate-300 text-base sm:text-lg mt-4 leading-relaxed">
            Where Michelin-caliber American gastronomy meets cutting-edge aerospace hospitality. 
            Immerse yourself in authentic barbecue, handcrafted cocktails, and intelligent AI concierge service.
          </p>
        </div>

        {/* 4 Feature Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, idx) => (
            <div 
              key={idx}
              className="group rounded-2xl glass-card p-6 border border-white/10 hover:border-cyan-500/40 transition-all duration-300 hover:shadow-neon-cyan flex flex-col justify-between"
            >
              <div>
                <div className="w-12 h-12 rounded-xl bg-cosmos-800 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider mb-1">
                  {feature.subtitle}
                </div>
                <h3 className="font-orbitron text-xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-4">
                  {feature.description}
                </p>
              </div>
              <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                <span className="text-[11px] font-mono text-slate-400 px-2.5 py-1 rounded-full bg-cosmos-900 border border-white/10">
                  {feature.highlight}
                </span>
                <Sparkles className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
              </div>
            </div>
          ))}
        </div>

        {/* Dedicated AI Concierge Banner & Access Prompt */}
        <div className="rounded-3xl glass-panel p-8 sm:p-10 border border-cyan-500/30 shadow-cosmic-card relative overflow-hidden">
          <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-gradient-to-br from-cyan-500/20 to-violet-600/20 rounded-full blur-3xl pointer-events-none" />
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            <div className="lg:col-span-8 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
                <Bot className="w-3.5 h-3.5 text-cyan-400" />
                <span>INTELLIGENT AI HOST • DEDICATED BEACON ACCESS</span>
              </div>
              <h3 className="font-orbitron text-2xl sm:text-3xl font-bold text-white">
                Have questions or need a custom reservation?
              </h3>
              <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl">
                Our Gemini AI Host is accessible at any moment from the floating beacon in the bottom-right corner of your screen. 
                Ask about specific table views, dietary accommodations, drink pairings, or check real-time availability in seconds.
              </p>
              <div className="flex flex-wrap items-center gap-3 pt-2 text-xs font-mono text-slate-400">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Online 24/7
                </span>
                <span className="text-slate-600">•</span>
                <span>Live Table Synchronization</span>
                <span className="text-slate-600">•</span>
                <span>Zero Latency SSE Streaming</span>
              </div>
            </div>

            <div className="lg:col-span-4 flex flex-col sm:flex-row lg:flex-col gap-3 justify-center items-stretch lg:items-end">
              <button
                onClick={onOpenChat}
                className="inline-flex items-center justify-center gap-2.5 px-6 py-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 hover:opacity-95 shadow-neon-cyan transition-all transform hover:-translate-y-0.5"
              >
                <Bot className="w-4 h-4 animate-bounce" />
                <span>Open AI Concierge Beacon</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <span className="text-[11px] font-mono text-slate-400 text-center lg:text-right">
                Or click the beacon button at the bottom right
              </span>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
