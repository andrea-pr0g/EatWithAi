import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  RotateCcw, 
  ShieldCheck, 
  ShieldAlert, 
  Maximize2, 
  Minimize2, 
  Copy, 
  Check, 
  Volume2, 
  VolumeX, 
  User, 
  Info
} from 'lucide-react';
import MarkdownMessage from './MarkdownMessage';

export default function FloatingChatWidget({ 
  messages, 
  isStreaming, 
  onSendMessage, 
  onResetChat,
  isOpen,
  setIsOpen,
  guardrailStatus,
  soundEnabled,
  setSoundEnabled
}) {
  const [inputText, setInputText] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [showTelemetry, setShowTelemetry] = useState(false);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of messages on new messages or streaming tokens
  useEffect(() => {
    if (isOpen && chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isOpen, isStreaming]);

  // Focus input field when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  // Handle keyboard shortcut (Escape to close)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, setIsOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const quickActionPrompts = [
    { label: "Book 2 for Tonight", prompt: "I'd like to book a table for 2 people tonight around 19:30." },
    { label: "Show Prime Steaks", prompt: "Tell me about the USDA Prime Ribeye and steaks on your menu." },
    { label: "Terrace Availability", prompt: "Do you have any outdoor terrace tables available this Friday at 20:00?" },
    { label: "Opening Hours", prompt: "What are your weekly flight times and lunch/dinner operating hours?" },
    { label: "Dietary & Vegan", prompt: "Which dishes on your menu are vegetarian, vegan, or gluten-free?" }
  ];

  return (
    <div className="fixed bottom-6 right-6 z-50">
      
      {/* Floating Launcher Button (When closed) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="relative group flex items-center gap-3 px-5 py-3.5 rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 text-white font-medium text-sm shadow-neon-cyan hover:shadow-neon-violet hover:scale-105 active:scale-95 transition-all duration-300 border border-white/20"
          aria-label="Open AI Concierge Chat"
        >
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-cosmos-950/80 flex items-center justify-center border border-cyan-300/40">
              <Bot className="w-4 h-4 text-cyan-300 animate-bounce" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-400"></span>
            </span>
          </div>

          <div className="flex flex-col items-start text-left">
            <span className="font-orbitron font-bold text-xs tracking-wider text-white">
              AI Concierge
            </span>
            <span className="text-[10px] font-mono text-cyan-200">
              Gemini 3.1 • Online
            </span>
          </div>

          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cosmos-950/60 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Ready
          </span>
        </button>
      )}

      {/* Floating Chat Window (When opened) */}
      {isOpen && (
        <div 
          className={`glass-panel border border-cyan-500/40 shadow-cosmic-card flex flex-col overflow-hidden transition-all duration-300 rounded-3xl ${
            isExpanded 
              ? 'w-[94vw] sm:w-[580px] h-[86vh] max-h-[760px]' 
              : 'w-[92vw] sm:w-[420px] h-[580px] max-h-[82vh]'
          }`}
        >
          
          {/* Header Bar */}
          <div className="px-4 py-3.5 bg-cosmos-950/95 border-b border-white/10 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="relative w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px] shadow-neon-cyan">
                <div className="w-full h-full bg-cosmos-900 rounded-xl flex items-center justify-center text-cyan-300">
                  <Bot className="w-4 h-4" />
                </div>
              </div>
              <div>
                <h4 className="font-orbitron text-xs font-bold text-white flex items-center gap-1.5">
                  <span>EatWithAi Concierge</span>
                  <span className="text-[10px] font-mono text-cyan-400 font-normal">LEO-1</span>
                </h4>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Gemini 3.1 Flash-Lite</span>
                  <span className="text-slate-600">•</span>
                  <button 
                    onClick={() => setShowTelemetry(!showTelemetry)} 
                    className="text-cyan-400 hover:underline flex items-center gap-0.5"
                    title="View Guardrails & Security Telemetry"
                  >
                    <span>Shielded</span>
                    <Info className="w-2.5 h-2.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Window Controls */}
            <div className="flex items-center gap-1">
              {setSoundEnabled && (
                <button
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  title={soundEnabled ? 'Mute Chimes' : 'Enable Chimes'}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-cyan-400" /> : <VolumeX className="w-3.5 h-3.5" />}
                </button>
              )}

              <button
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? 'Restore Standard Size' : 'Expand Chat Window'}
                className="hidden sm:inline-flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>

              <button
                onClick={onResetChat}
                title="Reset session & start fresh conversation"
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>

              <button
                onClick={() => setIsOpen(false)}
                title="Close chat beacon"
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Expandable Telemetry Drawer */}
          {showTelemetry && (
            <div className="px-4 py-2.5 bg-cosmos-900/95 border-b border-cyan-500/20 text-[11px] font-mono text-slate-300 animate-fadeIn shrink-0">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-cyan-300 font-semibold flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  Active Defense Architecture:
                </span>
                <span className="text-[10px] text-emerald-400">100% Protected</span>
              </div>
              <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                <span className="px-2 py-0.5 rounded bg-cosmos-950 text-cyan-300 border border-cyan-800/40">
                  ✓ Regex Pre-Filter
                </span>
                <span className="px-2 py-0.5 rounded bg-cosmos-950 text-violet-300 border border-violet-800/40">
                  ✓ Structural Isolation
                </span>
                <span className="px-2 py-0.5 rounded bg-cosmos-950 text-amber-300 border border-amber-800/40">
                  ✓ Confirmation Barrier
                </span>
                <span className="px-2 py-0.5 rounded bg-cosmos-950 text-emerald-300 border border-emerald-800/40">
                  ✓ Live DB Grounding
                </span>
              </div>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div 
            ref={chatContainerRef} 
            className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-cosmos-950/60 text-xs"
          >
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
              >
                {msg.role !== 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px] shadow-neon-cyan shrink-0 mt-0.5">
                    <div className="w-full h-full bg-cosmos-900 rounded-lg flex items-center justify-center text-cyan-300">
                      <Bot className="w-3.5 h-3.5" />
                    </div>
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 leading-relaxed relative group ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-tr-none shadow-neon-violet'
                      : 'bg-cosmos-900/90 border border-white/10 text-slate-200 rounded-tl-none shadow-cosmic-card'
                  }`}
                >
                  {/* Sender metadata & Copy button */}
                  <div className="text-[10px] font-mono mb-1 flex items-center justify-between text-slate-400">
                    <span className={msg.role === 'user' ? 'text-violet-200 font-medium' : 'text-cyan-400 font-semibold'}>
                      {msg.role === 'user' ? 'You' : 'AI Concierge'}
                    </span>
                    {msg.role !== 'user' && (
                      <button
                        onClick={() => handleCopy(msg.content, idx)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:text-cyan-300"
                        title="Copy message"
                      >
                        {copiedIndex === idx ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      </button>
                    )}
                  </div>

                  <div className="text-xs">
                    <MarkdownMessage content={msg.content} isBot={msg.role !== 'user'} />
                    {/* Blinking streaming cursor */}
                    {isStreaming && idx === messages.length - 1 && msg.role === 'bot' && (
                      <span className="animate-cursor" />
                    )}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-cosmos-800 border border-white/15 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5 text-slate-300" />
                  </div>
                )}
              </div>
            ))}

            {/* Guardrail Intervention Alert */}
            {guardrailStatus?.injection_detected && (
              <div className="p-3 rounded-xl bg-amber-950/50 border border-amber-500/40 text-amber-200 text-xs flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                <div>
                  <span className="font-semibold">[Guardrail Intervention]:</span> {guardrailStatus.reason || "Prompt injection blocked."} Refusal returned.
                </div>
              </div>
            )}
          </div>

          {/* Quick Action Suggestion Chips */}
          <div className="px-3 py-2 bg-cosmos-900/80 border-t border-white/5 flex gap-1.5 overflow-x-auto shrink-0">
            <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1 shrink-0 pl-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Prompts:
            </span>
            {quickActionPrompts.map((item, idx) => (
              <button
                key={idx}
                disabled={isStreaming}
                onClick={() => onSendMessage(item.prompt)}
                className="text-[10px] px-2.5 py-1 rounded-full bg-cosmos-800 hover:bg-cyan-950 text-slate-300 hover:text-cyan-300 border border-white/10 hover:border-cyan-500/40 transition-colors whitespace-nowrap disabled:opacity-40"
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <div className="p-3 bg-cosmos-950/95 border-t border-white/10 shrink-0">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isStreaming}
                placeholder={isStreaming ? "AI Concierge replying..." : "Ask tables, steaks, schedule, dietary..."}
                className="flex-1 bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isStreaming}
                className="px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 text-white font-medium text-xs hover:from-cyan-400 hover:to-violet-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-neon-cyan transition-colors shrink-0 flex items-center gap-1.5"
              >
                <span>Send</span>
                <Send className="w-3 h-3" />
              </button>
            </form>
            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mt-2 px-1">
              <span>Enter to transmit</span>
              <span>Explicit booking confirmation required</span>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
