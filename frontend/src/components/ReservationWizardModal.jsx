import React, { useState } from 'react';
import { 
  X, 
  Calendar, 
  Clock, 
  Users, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Bot, 
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function ReservationWizardModal({ isOpen, onClose, onHandoffToChat }) {
  const [step, setStep] = useState(1);
  const [partySize, setPartySize] = useState(2);
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [time, setTime] = useState('19:30');
  const [zone, setZone] = useState('indoor');
  
  // Customer info
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');

  // Status
  const [checking, setChecking] = useState(false);
  const [availabilityResult, setAvailabilityResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [bookingConfirmation, setBookingConfirmation] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleCheckAvailability = async (e) => {
    e.preventDefault();
    setChecking(true);
    setErrorMessage('');
    try {
      const res = await fetch('/api/check-availability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date,
          time,
          party_size: Number(partySize),
          zone: zone || undefined,
        })
      });
      const data = await res.json();
      setAvailabilityResult(data);
      if (data.available) {
        setStep(2);
      } else {
        setErrorMessage(data.reason || 'Requested time or table is not available.');
      }
    } catch (err) {
      setErrorMessage('Failed to connect to reservation engine: ' + err.message);
    } finally {
      setChecking(false);
    }
  };

  const handleConfirmReservation = async (e) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim()) {
      setErrorMessage('Full name and phone number are required.');
      return;
    }

    setSubmitting(true);
    setErrorMessage('');
    try {
      const res = await fetch('/api/reserve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: name,
          customer_phone: phone,
          customer_email: email || undefined,
          party_size: Number(partySize),
          date,
          time,
          zone_preference: zone,
          special_requests: specialRequests || undefined,
        })
      });
      const data = await res.json();
      if (data.booking_id) {
        setBookingConfirmation(data);
        setStep(3);
        // Trigger celebratory confetti
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b']
        });
      } else {
        setErrorMessage(data.message || 'Could not complete reservation.');
      }
    } catch (err) {
      setErrorMessage('Reservation failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleHandoff = () => {
    onClose();
    const prompt = `I'd like to book a table for ${partySize} guests on ${date} at ${time} in the ${zone} area. My name is ${name || 'Traveler'} and phone is ${phone || '+39 333 0000000'}.`;
    onHandoffToChat(prompt);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-cosmos-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-lg glass-panel rounded-3xl border border-cyan-500/30 shadow-cosmic-card overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-cosmos-950/90 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-cyan-400" />
            <h3 className="font-orbitron font-bold text-white text-base">
              Orbital Table Reservation
            </h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6">
          
          {/* Step 1: Time, Date & Zone Selector */}
          {step === 1 && (
            <form onSubmit={handleCheckAvailability} className="space-y-4">
              <p className="text-xs text-slate-300">
                Configure your flight party parameters to check table availability against the PostgreSQL engine:
              </p>

              {/* Date & Time */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Target Date</label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    required
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Time Slot</label>
                  <select
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="12:30">12:30 (Lunch)</option>
                    <option value="13:00">13:00 (Lunch)</option>
                    <option value="13:30">13:30 (Lunch)</option>
                    <option value="19:00">19:00 (Dinner)</option>
                    <option value="19:30">19:30 (Dinner)</option>
                    <option value="20:00">20:00 (Dinner)</option>
                    <option value="20:30">20:30 (Dinner)</option>
                    <option value="21:00">21:00 (Dinner)</option>
                  </select>
                </div>
              </div>

              {/* Party Size & Zone */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Party Size</label>
                  <select
                    value={partySize}
                    onChange={(e) => setPartySize(Number(e.target.value))}
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16].map((num) => (
                      <option key={num} value={num}>
                        {num} {num === 1 ? 'Guest (Solo)' : 'Guests'}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Preferred Zone</label>
                  <select
                    value={zone}
                    onChange={(e) => setZone(e.target.value)}
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="indoor">Indoor Nebula Lounge</option>
                    <option value="terrace">Starlight Covered Terrace</option>
                    <option value="bar">Meteorite Bar (1-2 guests)</option>
                    <option value="private_room">Orbital Private Suite (8-16)</option>
                  </select>
                </div>
              </div>

              {errorMessage && (
                <div className="p-3 rounded-xl bg-rose-950/50 border border-rose-500/40 text-xs text-rose-300 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={checking}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-medium text-sm shadow-neon-cyan flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {checking ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    <span>Checking Table Availability...</span>
                  </>
                ) : (
                  <>
                    <span>Verify Live Availability</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="text-center pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={handleHandoff}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-mono inline-flex items-center gap-1.5"
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span>Or let Gemini AI book it interactively</span>
                </button>
              </div>
            </form>
          )}

          {/* Step 2: Guest Details & Confirmation Barrier */}
          {step === 2 && (
            <form onSubmit={handleConfirmReservation} className="space-y-4">
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>
                  Tables verified! Party of {partySize} on {date} at {time} in {zone}. Stay duration: {availabilityResult?.dining_duration_minutes || 105} min.
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Full Name *</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Commander Shepard"
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">Phone Number *</label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+39 340 1234567"
                    className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1">Email (Optional)</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="traveler@orbit.com"
                  className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1">Special Requests (Dietary, Anniversary, etc.)</label>
                <textarea
                  rows={2}
                  value={specialRequests}
                  onChange={(e) => setSpecialRequests(e.target.value)}
                  placeholder="e.g. Celebrating 5th anniversary, window booth preferred"
                  className="w-full bg-cosmos-900 border border-white/15 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-400"
                />
              </div>

              {errorMessage && (
                <div className="p-3 rounded-xl bg-rose-950/50 border border-rose-500/40 text-xs text-rose-300">
                  {errorMessage}
                </div>
              )}

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-1/3 py-3 rounded-xl bg-cosmos-800 text-slate-300 text-xs font-mono hover:bg-cosmos-700 transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-2/3 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-medium text-sm shadow-neon-cyan flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {submitting ? 'Confirming...' : 'Lock In Reservation'}
                </button>
              </div>
            </form>
          )}

          {/* Step 3: Success Confirmation Screen */}
          {step === 3 && bookingConfirmation && (
            <div className="text-center py-4 space-y-4 animate-fadeIn">
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>

              <div>
                <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">
                  Orbital Flight Confirmed
                </span>
                <h4 className="font-orbitron text-xl font-bold text-white mt-1">
                  Table Locked & Secured!
                </h4>
              </div>

              <div className="p-4 rounded-xl bg-cosmos-900/90 border border-white/10 text-left text-xs font-mono space-y-2">
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Booking ID:</span>
                  <span className="text-cyan-300 font-bold">{bookingConfirmation.booking_id?.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Guest:</span>
                  <span className="text-white">{bookingConfirmation.customer?.name} ({bookingConfirmation.customer?.phone})</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Date & Time:</span>
                  <span className="text-white">{bookingConfirmation.date} at {bookingConfirmation.time}</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Party Size:</span>
                  <span className="text-white">{bookingConfirmation.party_size} guests</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Assigned Tables:</span>
                  <span className="text-emerald-300 font-bold">{bookingConfirmation.tables?.join(', ') || 'Auto-Allocated'}</span>
                </div>
              </div>

              <p className="text-xs text-slate-400">
                A confirmation has been saved directly into our PostgreSQL database. 
                Our Gemini AI Host can also review or cancel this booking at any time.
              </p>

              <button
                onClick={onClose}
                className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-cosmos-950 font-bold text-sm transition-all"
              >
                Done
              </button>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
