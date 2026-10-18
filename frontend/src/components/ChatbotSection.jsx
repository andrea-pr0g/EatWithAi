import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  Sparkles, 
  RotateCcw, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  Copy, 
  Check, 
  Terminal, 
  Cpu, 
  Layers, 
  Flame,
  UtensilsCrossed,
  Info
} from 'lucide-react';
import MarkdownMessage from './MarkdownMessage';

export default function ChatbotSection({ 
  messages, 
  isStreaming, 
  onSendMessage, 
  onResetChat, 
  guardrailStatus,
  soundEnabled 
}) {
  const [inputText, setInputText] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll internally inside the chat box without scrolling the browser page
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

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
    { label: "Book 2 for Dinner Tomorrow", prompt: "I'd like to book a table for 2 people tomorrow for dinner around 19:30." },
    { label: "Show Handcrafted Burgers", prompt: "Can you show me your handcrafted burgers and prices?" },
    { label: "Terrace Availability Friday", prompt: "Do you have any outdoor terrace tables available this Friday at 20:00?" },
    { label: "Weekly Opening Schedule", prompt: "What is your weekly opening schedule and lunch hours?" },
    { label: "Private Dining Room", prompt: "How many guests can the Private Room accommodate for a banquet?" },
    { label: "Gluten-Free & Vegan", prompt: "Which dishes on your menu are gluten-free or vegan?" },
  ];

  return (
    <section id="chatbot" className="py-20 relative overflow-hidden bg-cosmos-900/60 border-y border-white/5">
      {/* Decorative background glows */}
      <div className="absolute top-1/4 -left-48 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-48 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 text-xs font-mono mb-3">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>POWERED BY GOOGLE GENAI • GEMINI 3.1 FLASH-LITE</span>
          </div>
          <h2 className="font-orbitron text-3xl sm:text-4xl font-bold text-white tracking-wide">
            Galactic AI <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">Concierge</span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto mt-2">
            Ask questions, check real-time table availability across all 4 dining zones, 
            explore the menu, or secure your reservation with our guarded intelligent host.
          </p>
        </div>

        {/* Main Terminal Chat Container */}
        <div className="rounded-2xl glass-panel border border-white/10 shadow-cosmic-card overflow-hidden">
          
          {/* Terminal Top Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3.5 bg-cosmos-950/80 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
              </div>
              <div className="h-4 w-[1px] bg-white/15"></div>
              <span className="text-xs font-mono text-slate-300 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                <span>eatwithai-terminal // concierge-session</span>
              </span>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1 bg-emerald-950/60 border border-emerald-500/30 px-2.5 py-1 rounded-md">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                LIVE SSE STREAMING
              </span>

              <button
                onClick={onResetChat}
                className="flex items-center gap-1 text-xs font-mono text-slate-400 hover:text-white px-2.5 py-1 rounded-md bg-white/5 hover:bg-white/10 transition-colors"
                title="Reset session & start fresh conversation"
              >
                <RotateCcw className="w-3 h-3 text-slate-400" />
                <span>Reset</span>
              </button>
            </div>
          </div>

          {/* Active Guardrails Banner (Directly matches run_chatbot.py) */}
          <div className="px-5 py-3 bg-cosmos-900/90 border-b border-white/5 text-xs text-slate-400 font-mono">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-slate-300 font-semibold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                Active Defense Layers:
              </span>
              <div className="flex flex-wrap gap-2 text-[11px]">
                <span className="px-2 py-0.5 rounded bg-cyan-950/50 text-cyan-300 border border-cyan-800/40">
                  [x] Regex Pre-Filtering
                </span>
                <span className="px-2 py-0.5 rounded bg-violet-950/50 text-violet-300 border border-violet-800/40">
                  [x] &lt;untrusted_customer_message&gt; Isolation
                </span>
                <span className="px-2 py-0.5 rounded bg-amber-950/50 text-amber-300 border border-amber-800/40">
                  [x] Confirmation Barrier
                </span>
                <span className="px-2 py-0.5 rounded bg-emerald-950/50 text-emerald-300 border border-emerald-800/40">
                  [x] Live DB Grounding
                </span>
              </div>
            </div>
          </div>

          {/* Chat Messages Log */}
          <div ref={chatContainerRef} className="h-[460px] overflow-y-auto p-5 sm:p-6 space-y-4 bg-cosmos-950/40">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-3 sm:gap-4 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                } animate-fadeIn`}
              >
                {msg.role !== 'user' && (
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px] shadow-neon-cyan shrink-0">
                    <div className="w-full h-full bg-cosmos-900 rounded-xl flex items-center justify-center">
                      <Bot className="w-4 h-4 text-cyan-300" />
                    </div>
                  </div>
                )}

                <div className={`max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 sm:px-5 py-3.5 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-neon-violet ml-auto rounded-tr-none'
                    : 'glass-card border border-white/10 text-slate-100 rounded-tl-none shadow-cosmic-card relative group'
                }`}>
                  {/* Sender Label */}
                  <div className="text-[10px] font-mono mb-1.5 flex items-center justify-between text-slate-400">
                    <span className={msg.role === 'user' ? 'text-violet-200' : 'text-cyan-400 font-semibold'}>
                      {msg.role === 'user' ? 'Guest Traveler' : 'EatWithAi Host'}
                    </span>
                    {msg.role !== 'user' && (
                      <button
                        onClick={() => handleCopy(msg.content, idx)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-cyan-300"
                        title="Copy message"
                      >
                        {copiedIndex === idx ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      </button>
                    )}
                  </div>

                  {/* Render Message Body with marked & dompurify */}
                  <div className="text-sm">
                    <MarkdownMessage content={msg.content} isBot={msg.role !== 'user'} />
                    {/* Blinking cursor for actively streaming bot message */}
                    {isStreaming && idx === messages.length - 1 && msg.role === 'bot' && (
                      <span className="animate-cursor" />
                    )}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-9 h-9 rounded-xl bg-cosmos-800 border border-white/15 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>
                )}
              </div>
            ))}

            {/* Guardrail Trigger Notification (if flagged) */}
            {guardrailStatus?.injection_detected && (
              <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/40 text-amber-200 text-xs flex items-center gap-2.5">
                <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
                <div>
                  <span className="font-semibold">[GUARDRAIL INTERVENTION]</span> Input intercepted: {guardrailStatus.reason || "Prompt injection attempt detected"}. Clean refusal dispatched.
                </div>
              </div>
            )}
          </div>

          {/* Quick Action Chips Bar */}
          <div className="p-3 bg-cosmos-900/70 border-t border-white/5 overflow-x-auto">
            <div className="flex items-center gap-2 min-w-max">
              <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1 pl-2">
                <Sparkles className="w-3 h-3 text-cyan-400" />
                Suggestions:
              </span>
              {quickActionPrompts.map((item, idx) => (
                <button
                  key={idx}
                  disabled={isStreaming}
                  onClick={() => onSendMessage(item.prompt)}
                  className="text-xs px-3 py-1 rounded-full bg-cosmos-800/80 hover:bg-cyan-950 text-slate-300 hover:text-cyan-300 border border-white/10 hover:border-cyan-500/40 transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Message Input Box */}
          <div className="p-4 bg-cosmos-950/90 border-t border-white/10">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isStreaming}
                placeholder={isStreaming ? "AI Host is transmitting live..." : "Type your reservation inquiry or question... (e.g. 'Table for 2 tonight')"}
                className="flex-1 bg-cosmos-900/90 text-slate-100 placeholder-slate-500 text-sm px-4 py-3 rounded-xl border border-white/15 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isStreaming}
                className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium text-sm flex items-center gap-2 shadow-neon-cyan transition-all shrink-0"
              >
                <span>Send</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-2 px-1">
              <span>Strict Data Boundary Isolation Active</span>
              <span>Confirmation required prior to database booking</span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
