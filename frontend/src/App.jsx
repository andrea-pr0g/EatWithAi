import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import ChatbotSection from './components/ChatbotSection';
import MenuSection from './components/MenuSection';
import ZonesSection from './components/ZonesSection';
import ScheduleSection from './components/ScheduleSection';
import ReservationWizardModal from './components/ReservationWizardModal';
import FloatingChatWidget from './components/FloatingChatWidget';
import Footer from './components/Footer';

// Web Audio API soft cosmic chime synthesizer
const playCosmicChime = () => {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.15); // A5

    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.6);
  } catch (e) {
    // Ignore audio permission or context restrictions
  }
};

export default function App() {
  const [sessionId] = useState(() => {
    let sid = localStorage.getItem('eatwithai_session_id');
    if (!sid) {
      sid = 'session_' + Math.random().toString(36).substring(2, 12);
      localStorage.setItem('eatwithai_session_id', sid);
    }
    return sid;
  });

  const initialBotGreeting = {
    role: 'bot',
    content: "Greetings traveler! I am **EatWithAi Host**, your dedicated Gemini AI reservation concierge aboard Orbital Platform 1.\n\nWhether you're craving our **USDA Prime Ribeye Steak**, 14-hour **Texas Post-Oak Smoked Brisket**, or handcrafted smash burgers while gazing down at planet Earth, I'm here to assist you.\n\nHow can I help with your table reservations, dining zones, or menu questions today?"
  };

  const [messages, setMessages] = useState([initialBotGreeting]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [guardrailStatus, setGuardrailStatus] = useState(null);
  const [statusInfo, setStatusInfo] = useState(null);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [wizardOpen, setWizardOpen] = useState(false);

  // Fetch restaurant live status & schedule on load
  useEffect(() => {
    fetch('/api/restaurant-info')
      .then(res => res.json())
      .then(data => setStatusInfo(data))
      .catch(err => console.error("Could not fetch restaurant status:", err));
  }, []);

  // Send message with real-time SSE streaming
  const handleSendMessage = useCallback(async (userText) => {
    if (!userText.trim() || isStreaming) return;

    // 1. Add user message
    setMessages(prev => [
      ...prev,
      { role: 'user', content: userText },
      { role: 'bot', content: '' } // Placeholder for streaming tokens
    ]);
    setIsStreaming(true);
    setGuardrailStatus(null);

    // Scroll smoothly to chatbot section if not already in view
    const chatEl = document.getElementById('chatbot');
    if (chatEl && window.scrollY < 200) {
      chatEl.scrollIntoView({ behavior: 'smooth' });
    }

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userText
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Retain partial trailing chunk

        for (const ev of events) {
          if (!ev.trim()) continue;
          const lines = ev.split('\n');
          let eventType = 'message';
          let dataStr = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.substring(7).trim();
            } else if (line.startsWith('data: ')) {
              dataStr = line.substring(6).trim();
            }
          }

          if (eventType === 'guardrails') {
            try {
              const guardData = JSON.parse(dataStr);
              setGuardrailStatus(guardData);
            } catch (e) {}
          } else if (eventType === 'token') {
            try {
              const tokenData = JSON.parse(dataStr);
              if (tokenData.chunk) {
                setMessages(prev => {
                  const updated = [...prev];
                  const lastIndex = updated.length - 1;
                  if (lastIndex >= 0 && updated[lastIndex].role === 'bot') {
                    updated[lastIndex] = {
                      ...updated[lastIndex],
                      content: updated[lastIndex].content + tokenData.chunk
                    };
                  }
                  return updated;
                });
              }
            } catch (e) {}
          } else if (eventType === 'error') {
            try {
              const errData = JSON.parse(dataStr);
              setMessages(prev => {
                const updated = [...prev];
                const lastIndex = updated.length - 1;
                updated[lastIndex] = {
                  ...updated[lastIndex],
                  content: `[Communication Glitch]: ${errData.error || 'Unknown error'}`
                };
                return updated;
              });
            } catch (e) {}
          }
        }
      }

      if (soundEnabled) {
        playCosmicChime();
      }
    } catch (err) {
      console.error('Chat transmission error:', err);
      setMessages(prev => {
        const updated = [...prev];
        const lastIndex = updated.length - 1;
        updated[lastIndex] = {
          ...updated[lastIndex],
          content: "I apologize, but my connection to the orbital communications array was interrupted. Please try asking again."
        };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [sessionId, isStreaming, soundEnabled]);

  const handleResetChat = async () => {
    try {
      await fetch('/api/chat/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
    } catch (e) {}
    setMessages([initialBotGreeting]);
    setGuardrailStatus(null);
  };

  return (
    <div className="min-h-screen bg-cosmos-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      
      {/* Navigation Bar */}
      <Navbar 
        onOpenChat={() => {
          document.getElementById('chatbot')?.scrollIntoView({ behavior: 'smooth' });
        }}
        statusInfo={statusInfo}
        soundEnabled={soundEnabled}
        setSoundEnabled={setSoundEnabled}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        
        {/* Hero Section */}
        <Hero 
          onSendMessage={handleSendMessage}
          onOpenWizard={() => setWizardOpen(true)}
        />

        {/* The Core Chatbot Terminal Section */}
        <ChatbotSection 
          messages={messages}
          isStreaming={isStreaming}
          onSendMessage={handleSendMessage}
          onResetChat={handleResetChat}
          guardrailStatus={guardrailStatus}
          soundEnabled={soundEnabled}
        />

        {/* Database-Grounded Menu Section */}
        <MenuSection 
          onAskAboutDish={handleSendMessage}
        />

        {/* Station Dining Zones Section */}
        <ZonesSection 
          onSelectZone={(zoneName) => {
            handleSendMessage(`Tell me about the ${zoneName} and check if you have tables available there tonight or tomorrow.`);
          }}
          onOpenWizard={() => setWizardOpen(true)}
        />

        {/* Flight Schedule & Operating Hours */}
        <ScheduleSection 
          scheduleInfo={statusInfo}
        />

      </main>

      {/* Footer */}
      <Footer />

      {/* Floating Chat Widget (bottom-right orb for quick chat anywhere on page) */}
      <FloatingChatWidget 
        messages={messages}
        isStreaming={isStreaming}
        onSendMessage={handleSendMessage}
        onResetChat={handleResetChat}
      />

      {/* Visual Reservation Wizard Modal */}
      <ReservationWizardModal 
        isOpen={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onHandoffToChat={handleSendMessage}
      />

    </div>
  );
}
