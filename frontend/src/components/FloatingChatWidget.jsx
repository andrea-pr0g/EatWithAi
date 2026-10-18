import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  MessageSquare, 
  Minimize2, 
  Maximize2,
  RotateCcw,
  ShieldCheck
} from 'lucide-react';
import MarkdownMessage from './MarkdownMessage';

export default function FloatingChatWidget({ 
  messages, 
  isStreaming, 
  onSendMessage, 
  onResetChat 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (isOpen && chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isOpen, isStreaming]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const samplePrompts = [
    "Table for 2 tonight",
    "Show me burgers",
    "Are you open Monday?"
  ];

  return (
    <div className="fixed bottom-6 right-6 z-40">
      
      {/* Floating Toggle Button (When closed) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="relative group flex items-center gap-3 px-5 py-3.5 rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 text-white font-medium text-sm shadow-neon-cyan hover:shadow-neon-violet hover:scale-105 transition-all duration-300"
          aria-label="Open AI Concierge Chat"
        >
          <div className="relative">
            <Bot className="w-5 h-5 animate-bounce" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-300 animate-ping"></span>
          </div>
          <span className="font-orbitron font-semibold text-xs tracking-wider">
            AI Concierge
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cosmos-950/60 text-cyan-200 border border-cyan-400/30">
            Online
          </span>
        </button>
      )}

      {/* Floating Chat Modal (When open) */}
      {isOpen && (
        <div className="w-[92vw] sm:w-[400px] h-[520px] rounded-3xl glass-panel border border-cyan-500/40 shadow-cosmic-card flex flex-col overflow-hidden animate-fadeIn">
          
          {/* Header */}
          <div className="px-4 py-3 bg-cosmos-950/90 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-300">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-orbitron text-xs font-bold text-white">EatWithAi Concierge</h4>
                <div className="flex items-center gap-1.5 text-[10px] text-cyan-400 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Gemini 3.1 Flash-Lite</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={onResetChat}
                title="Reset session"
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Close chat window"
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3 bg-cosmos-950/40 text-xs">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role !== 'user' && (
                  <div className="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/30 flex items-center justify-center text-cyan-300 shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-xl px-3 py-2 leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-violet-600 text-white rounded-tr-none'
                      : 'bg-cosmos-900 border border-white/10 text-slate-200 rounded-tl-none'
                  }`}
                >
                  <div className="text-xs">
                    <MarkdownMessage content={msg.content} isBot={msg.role !== 'user'} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Suggestions Chips */}
          <div className="px-3 py-2 bg-cosmos-900/60 border-t border-white/5 flex gap-1.5 overflow-x-auto">
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                disabled={isStreaming}
                onClick={() => onSendMessage(p)}
                className="text-[10px] px-2.5 py-1 rounded-full bg-cosmos-800 text-slate-300 hover:text-cyan-300 border border-white/10 whitespace-nowrap transition-colors"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="p-3 bg-cosmos-950/90 border-t border-white/10 flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isStreaming}
              placeholder={isStreaming ? "AI Host replying..." : "Ask reservation host..."}
              className="flex-1 bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isStreaming}
              className="p-2 rounded-xl bg-cyan-500 text-cosmos-950 hover:bg-cyan-400 disabled:opacity-40 transition-colors shrink-0"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>

        </div>
      )}

    </div>
  );
}
