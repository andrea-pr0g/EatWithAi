import React from 'react';
import { 
  Sparkles, 
  Bot, 
  Orbit, 
  ShieldCheck, 
  Compass, 
  Heart
} from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative bg-cosmos-950 border-t border-white/10 pt-16 pb-12 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 pb-12 border-b border-white/10">
          
          {/* Col 1: Brand & Space Mission */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px] shadow-neon-cyan">
                <div className="w-full h-full bg-cosmos-900 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-cyan-400" />
                </div>
              </div>
              <span className="font-orbitron font-bold text-2xl tracking-wider text-white">
                EatWith<span className="text-cyan-400">Ai</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed">
              Orbital Station 1 • Earth Low Orbit (408 km). Serving authentic American prime steaks, 
              post-oak smoked BBQ, and handcrafted burgers above the clouds. Fully integrated with 
              Gemini AI reservation intelligence and multi-layer prompt defense.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Guardrails: Regex Pre-Filter • Structural Delimiters • Confirmation Barrier</span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="space-y-3">
            <h4 className="font-orbitron text-xs font-bold uppercase tracking-widest text-slate-200">
              Orbital Station
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#chatbot" className="hover:text-cyan-400 transition-colors">Gemini AI Concierge</a></li>
              <li><a href="#menu" className="hover:text-cyan-400 transition-colors">Menu</a></li>
              <li><a href="#zones" className="hover:text-cyan-400 transition-colors">Dining Zones & Tables</a></li>
              <li><a href="#schedule" className="hover:text-cyan-400 transition-colors">Flight Schedule & Shifts</a></li>
            </ul>
          </div>

          {/* Col 3: Architecture Stack */}
          <div className="space-y-3">
            <h4 className="font-orbitron text-xs font-bold uppercase tracking-widest text-slate-200">
              Engineered With
            </h4>
            <ul className="space-y-2 text-xs font-mono text-slate-400">
              <li className="flex items-center gap-1.5 text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                Google Gemini 3.1 Flash-Lite
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
                PostgreSQL Reservation Engine
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                FastAPI Real-time SSE
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                Tailwind CSS v3 & React Vite
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
          <p>© {new Date().getFullYear()} EatWithAi Orbital Gastronomy. All cosmic rights reserved.</p>
          <p className="flex items-center gap-1">
            <span>Powered by</span>
            <span className="text-cyan-400 font-semibold">Gemini AI</span>
            <span>&</span>
            <span className="text-violet-400 font-semibold">PostgreSQL</span>
          </p>
        </div>

      </div>
    </footer>
  );
}
