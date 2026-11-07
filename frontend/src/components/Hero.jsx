import React from 'react';
import { 
  Bot, 
  Calendar, 
  UtensilsCrossed,
  ArrowRight
} from 'lucide-react';

export default function Hero({ onOpenWizard, onOpenChat }) {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center pt-24 pb-16 overflow-hidden cosmic-stars">
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
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>ORBITAL PLATFORM 1 • EARTH ELEVATION 408 KM</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          <span className="text-slate-300">GEMINI 3.1 AI HOST ACTIVE</span>
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
          wood-smoked <span className="text-violet-300 font-medium">Texas BBQ</span>, and handcrafted smash burgers 
          while gazing down at planet Earth from 408 km above.
        </p>

        {/* Primary Call-to-Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10 max-w-xl mx-auto">
          <button
            onClick={onOpenWizard}
            className="w-full sm:w-auto flex-1 inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 hover:opacity-95 shadow-neon-cyan transition-all transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <Calendar className="w-5 h-5" />
            <span>Book a Table Now</span>
          </button>
          
          <a
            href="#menu"
            className="w-full sm:w-auto flex-1 inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-slate-200 glass-card hover:bg-white/10 border border-white/15 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <UtensilsCrossed className="w-5 h-5 text-cyan-400" />
            <span>Explore Menu</span>
          </a>
        </div>

        {/* Single Bot Concierge Beacon Hint */}
        <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full glass-card border border-white/10 text-xs text-slate-300 mb-14 hover:border-cyan-500/30 transition-colors">
          <div className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center">
            <Bot className="w-3.5 h-3.5" />
          </div>
          <span>Have questions about dishes or tables? Talk to our AI Concierge using the beacon in the bottom-right corner.</span>
          <button
            onClick={onOpenChat}
            className="text-cyan-400 hover:text-cyan-300 font-medium font-mono text-[11px] underline flex items-center gap-0.5 ml-1"
          >
            <span>Open Chat</span>
            <ArrowRight className="w-3 h-3" />
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
