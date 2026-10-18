import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Bot, 
  Calendar, 
  UtensilsCrossed, 
  Layers, 
  Clock, 
  Menu as MenuIcon, 
  X, 
  Compass,
  Volume2,
  VolumeX
} from 'lucide-react';

export default function Navbar({ onOpenChat, statusInfo, soundEnabled, setSoundEnabled }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isOpen = statusInfo?.status?.is_open ?? true;
  const shiftName = statusInfo?.status?.shift?.name || 'Dinner Service';

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled 
        ? 'bg-cosmos-950/85 backdrop-blur-md border-b border-white/10 shadow-2xl py-3' 
        : 'bg-transparent py-5'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          
          {/* Logo & Orbital Station Brand */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px] shadow-neon-cyan transition-transform group-hover:scale-105">
              <div className="w-full h-full bg-cosmos-900 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400 group-hover:rotate-12 transition-transform" />
              </div>
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-orbitron font-bold text-xl tracking-wider text-white">
                  EatWith<span className="text-cyan-400">Ai</span>
                </span>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-300 border border-cyan-500/30">
                  Orbit LEO
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${isOpen ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`}></span>
                {isOpen ? `Station Open • ${shiftName}` : 'Station Closed'}
              </p>
            </div>
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8">
            <a 
              href="#chatbot" 
              className="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5"
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              AI Concierge
            </a>
            <a 
              href="#menu" 
              className="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5"
            >
              <UtensilsCrossed className="w-4 h-4 text-violet-400" />
              Menu
            </a>
            <a 
              href="#zones" 
              className="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5"
            >
              <Layers className="w-4 h-4 text-cyan-400" />
              Dining Zones
            </a>
            <a 
              href="#schedule" 
              className="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5"
            >
              <Clock className="w-4 h-4 text-amber-400" />
              Hours & Schedule
            </a>
          </nav>

          {/* Action Buttons */}
          <div className="hidden sm:flex items-center gap-3">
            {/* Audio Toggle */}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              title={soundEnabled ? 'Mute AI Audio Signals' : 'Enable AI Audio Signals'}
              className="p-2.5 rounded-xl border border-white/10 bg-cosmos-800/60 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/30 transition-all"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4 text-cyan-400" /> : <VolumeX className="w-4 h-4" />}
            </button>

            {/* Launch AI Concierge Button */}
            <button
              onClick={onOpenChat}
              className="relative inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-cyan-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 shadow-neon-cyan hover:shadow-neon-violet transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
            >
              <Bot className="w-4 h-4 animate-bounce" />
              <span>Launch Gemini Concierge</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-cosmos-800/80 text-slate-200 border border-white/10"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-b border-white/10 px-4 pt-4 pb-6 mt-3 space-y-4 animate-fadeIn">
          <nav className="flex flex-col gap-3">
            <a 
              href="#chatbot" 
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 p-3 rounded-lg bg-cosmos-800/50 text-slate-200"
            >
              <Bot className="w-5 h-5 text-cyan-400" />
              AI Reservation Concierge
            </a>
            <a 
              href="#menu" 
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 p-3 rounded-lg bg-cosmos-800/50 text-slate-200"
            >
              <UtensilsCrossed className="w-5 h-5 text-violet-400" />
              Menu
            </a>
            <a 
              href="#zones" 
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 p-3 rounded-lg bg-cosmos-800/50 text-slate-200"
            >
              <Layers className="w-5 h-5 text-cyan-400" />
              Dining Zones & Tables
            </a>
            <a 
              href="#schedule" 
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 p-3 rounded-lg bg-cosmos-800/50 text-slate-200"
            >
              <Clock className="w-5 h-5 text-amber-400" />
              Flight Schedule & Shifts
            </a>
          </nav>

          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenChat();
            }}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-violet-600 text-white font-medium flex items-center justify-center gap-2 shadow-neon-cyan"
          >
            <Bot className="w-5 h-5" />
            Launch Gemini Concierge
          </button>
        </div>
      )}
    </header>
  );
}
