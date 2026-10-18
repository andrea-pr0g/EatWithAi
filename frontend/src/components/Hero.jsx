import React, { useState } from 'react';
import { 
  Bot, 
  Sparkles, 
  Calendar, 
  ShieldCheck, 
  ChevronRight, 
  Orbit, 
  ArrowRight,
  Flame,
  Award
} from 'lucide-react';

export default function Hero({ onSendMessage, onOpenWizard }) {
  const [quickInput, setQuickInput] = useState('');

  const handleQuickSubmit = (e) => {
    e.preventDefault();
    if (!quickInput.trim()) return;
    onSendMessage(quickInput.trim());
    setQuickInput('');
  };

  const samplePrompts = [
    "Book a table for 2 tonight at 19:30",
    "Show me the USDA Prime Ribeye Steak",
    "Is the Covered Terrace available Friday?",
    "What are your opening hours on weekends?"
  ];

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-24 pb-16 overflow-hidden cosmic-stars">
      {/* Background Graphic & Dark Cosmic Gradient Overlays */}
      <div className="absolute inset-0 z-0">
        <img 
          src="/assets/restaurant-hero.jpg" 
          alt="EatWithAi Space Restaurant Panoramic Interior"
          className="w-full h-full object-cover object-center opacity-30 mix-blend-luminosity scale-105 transform motion-safe:animate-pulse-slow"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-cosmos-950 via-cosmos-950/80 to-cosmos-950" />
        <div className="absolute inset-0 bg-radial-gradient from-cyan-500/10 via-violet-900/15 to-transparent pointer-events-none" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        
        {/* Orbital Station Badge */}
        <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full glass-panel border border-cyan-500/30 text-cyan-300 text-xs sm:text-sm font-mono mb-8 shadow-neon-cyan animate-float-slow">
          <Orbit className="w-4 h-4 text-cyan-400 animate-spin" style={{ animationDuration: '10s' }} />
          <span>ORBITAL PLATFORM 1 • EARTH ELEVATION 408 KM</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          <span className="text-slate-300">GEMINI 3.1 AI RESERVATION AGENT ACTIVE</span>
        </div>

        {/* Main Hero Headline */}
        <h1 className="font-orbitron text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          FEAST AMONG <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400 bg-clip-text text-transparent text-glow-cyan">
            THE STARS
          </span>
        </h1>

        {/* Subtitle */}
        <p className="max-w-3xl mx-auto text-base sm:text-lg md:text-xl text-slate-300 font-light mb-10 leading-relaxed">
          Welcome to <span className="text-white font-medium">EatWithAi</span>, the world’s first orbital restaurant. 
          Indulge in authentic <span className="text-cyan-300 font-medium">USDA Prime steaks</span>, 
          wood-smoked <span className="text-violet-300 font-medium">Texas BBQ</span>, and handcrafted burgers 
          while viewing the blue marble below. Managed by an intelligent Gemini reservation concierge.
        </p>

        {/* Interactive Quick AI Prompt Bar */}
        <div className="max-w-2xl mx-auto mb-6">
          <form 
            onSubmit={handleQuickSubmit}
            className="relative flex items-center p-2 rounded-2xl glass-panel border border-cyan-500/40 shadow-cosmic-card focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/30 transition-all"
          >
            <div className="pl-3 pr-2 text-cyan-400">
              <Bot className="w-6 h-6 animate-pulse" />
            </div>
            <input 
              type="text"
              value={quickInput}
              onChange={(e) => setQuickInput(e.target.value)}
              placeholder="Ask the AI Host anything... (e.g. 'Table for 4 this Saturday at 8 PM')"
              className="w-full bg-transparent border-none text-slate-100 placeholder-slate-400 text-sm sm:text-base focus:outline-none focus:ring-0 py-2"
            />
            <button
              type="submit"
              className="flex items-center gap-1.5 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-medium text-sm transition-all shadow-neon-cyan shrink-0"
            >
              <span>Ask Host</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 max-w-3xl mx-auto mb-12">
          <span className="text-xs text-slate-400 font-mono flex items-center gap-1 mr-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Quick Prompts:
          </span>
          {samplePrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt)}
              className="text-xs px-3.5 py-1.5 rounded-full bg-cosmos-800/80 hover:bg-cosmos-700/90 text-slate-300 hover:text-cyan-300 border border-white/10 hover:border-cyan-500/40 transition-all duration-200"
            >
              "{prompt}"
            </button>
          ))}
        </div>

        {/* Primary CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <a
            href="#chatbot"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 hover:opacity-95 shadow-neon-cyan transition-all transform hover:-translate-y-0.5"
          >
            <Bot className="w-5 h-5" />
            Chat with Gemini Concierge
          </a>
          <button
            onClick={onOpenWizard}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-slate-200 glass-card hover:bg-white/10 border border-white/15 transition-all transform hover:-translate-y-0.5"
          >
            <Calendar className="w-5 h-5 text-cyan-400" />
            Direct Visual Booking
          </button>
        </div>

        {/* Telemetry Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto pt-6 border-t border-white/10">
          <div className="p-4 rounded-xl glass-card text-center">
            <div className="text-2xl sm:text-3xl font-orbitron font-bold text-cyan-400">408 km</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Orbital Elevation</div>
          </div>
          <div className="p-4 rounded-xl glass-card text-center">
            <div className="text-2xl sm:text-3xl font-orbitron font-bold text-violet-400">35 Dishes</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Menu Specialties</div>
          </div>
          <div className="p-4 rounded-xl glass-card text-center">
            <div className="text-2xl sm:text-3xl font-orbitron font-bold text-amber-400">4 Zones</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Terrace, Hall, Bar, VIP</div>
          </div>
          <div className="p-4 rounded-xl glass-card text-center">
            <div className="text-2xl sm:text-3xl font-orbitron font-bold text-emerald-400">4 Layers</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Active AI Defense Guardrails</div>
          </div>
        </div>

      </div>
    </section>
  );
}
