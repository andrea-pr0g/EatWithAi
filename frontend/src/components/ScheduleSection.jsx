import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Calendar, 
  AlertTriangle, 
  MapPin, 
  ShieldCheck, 
  Orbit, 
  CheckCircle,
  Radio
} from 'lucide-react';

export default function ScheduleSection({ scheduleInfo }) {
  const weekly = scheduleInfo?.schedule?.weekly_schedule || [
    { day: 'Monday', shift: 'lunch', hours: '12:00 - 15:00', last_bookable: '14:00' },
    { day: 'Monday', shift: 'dinner', hours: '19:00 - 23:00', last_bookable: '21:30' },
    { day: 'Tuesday', shift: 'lunch', hours: '12:00 - 15:00', last_bookable: '14:00' },
    { day: 'Tuesday', shift: 'dinner', hours: '19:00 - 23:00', last_bookable: '21:30' },
    { day: 'Wednesday', shift: 'lunch', hours: '12:00 - 15:00', last_bookable: '14:00' },
    { day: 'Wednesday', shift: 'dinner', hours: '19:00 - 23:00', last_bookable: '21:30' },
    { day: 'Thursday', shift: 'lunch', hours: '12:00 - 15:00', last_bookable: '14:00' },
    { day: 'Thursday', shift: 'dinner', hours: '19:00 - 23:30', last_bookable: '22:00' },
    { day: 'Friday', shift: 'lunch', hours: '12:00 - 15:00', last_bookable: '14:00' },
    { day: 'Friday', shift: 'dinner', hours: '19:00 - 23:59', last_bookable: '22:30' },
    { day: 'Saturday', shift: 'lunch', hours: '12:00 - 15:30', last_bookable: '14:15' },
    { day: 'Saturday', shift: 'dinner', hours: '19:00 - 23:59', last_bookable: '22:30' },
    { day: 'Sunday', shift: 'lunch', hours: '12:00 - 16:00', last_bookable: '14:30' },
    { day: 'Sunday', shift: 'dinner', hours: '19:00 - 23:00', last_bookable: '21:30' },
  ];

  const closures = scheduleInfo?.schedule?.upcoming_closures || [
    { date: '2026-11-01', reason: 'All Saints Day (Full Day Holiday)' },
    { date: '2026-11-20', reason: 'Private Gala Dinner on Friday Night' },
    { date: '2026-12-25', reason: 'Christmas Day (Full Day Holiday)' },
    { date: '2026-12-26', reason: 'St. Stephen Day Lunch (Kitchen Deep Cleaning)' }
  ];

  // Group by day
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <section id="schedule" className="py-24 relative bg-cosmos-900/40 border-t border-white/5 cosmic-stars">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-950/70 border border-amber-500/40 text-amber-300 text-xs font-mono mb-4">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>MISSION OPERATING HOURS & SHIFTS</span>
          </div>
          <h2 className="font-orbitron text-3xl sm:text-5xl font-extrabold text-white tracking-wide">
            Flight Schedule & <span className="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">Hours</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg mt-3">
            Open 7 days a week for orbital lunch and starlight dinner services.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Weekly Schedule Table (Left 8 cols) */}
          <div className="lg:col-span-8 glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 shadow-cosmic-card">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <h3 className="font-orbitron text-xl font-bold text-white flex items-center gap-2">
                <Calendar className="w-5 h-5 text-cyan-400" />
                <span>Weekly Flight Times</span>
              </h3>
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1.5 bg-emerald-950/60 border border-emerald-500/30 px-3 py-1 rounded-full">
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                Live UTC+2 Ground Time
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {days.map((day) => {
                const dayShifts = weekly.filter(s => s.day === day);
                return (
                  <div key={day} className="p-4 rounded-xl bg-cosmos-900/80 border border-white/5 space-y-2">
                    <div className="font-orbitron text-sm font-semibold text-cyan-300 flex items-center justify-between">
                      <span>{day}</span>
                      <span className="text-[10px] font-mono text-slate-400">2 Services</span>
                    </div>
                    {dayShifts.map((shift, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs font-mono text-slate-300 pt-1 border-t border-white/5">
                        <span className="capitalize text-slate-400">{shift.shift}:</span>
                        <span className="text-white font-medium">{shift.hours}</span>
                        <span className="text-[10px] text-amber-400/90">(cutoff {shift.last_bookable})</span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Upcoming Closures & Station Info (Right 4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Closures Alert Box */}
            <div className="glass-panel rounded-3xl p-6 border border-amber-500/30 shadow-cosmic-card">
              <div className="flex items-center gap-2 text-amber-400 font-orbitron text-base font-bold mb-4">
                <AlertTriangle className="w-5 h-5" />
                <span>Mission Closures & Galas</span>
              </div>
              <p className="text-xs text-slate-300 mb-4">
                The restaurant will be offline for private functions and orbital maintenance on the following dates:
              </p>
              <div className="space-y-3">
                {closures.map((c, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs">
                    <div className="font-mono font-semibold text-amber-300">{c.date}</div>
                    <div className="text-slate-300 text-[11px] mt-0.5">{c.reason}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Orbital Station Coordinates */}
            <div className="glass-panel rounded-3xl p-6 border border-white/10 space-y-4">
              <div className="flex items-center gap-2 text-cyan-400 font-orbitron text-base font-bold">
                <Orbit className="w-5 h-5" />
                <span>Station Coordinates</span>
              </div>
              <div className="text-xs font-mono space-y-2 text-slate-300">
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Position:</span>
                  <span>Low Earth Orbit (LEO)</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Shuttle Docking:</span>
                  <span className="text-cyan-300">Airlock Alpha-7</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-1">
                  <span className="text-slate-400">Atmosphere:</span>
                  <span>1.0 ATM (Sea Level Mix)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Gravity:</span>
                  <span>0.98G (Simulated Spin)</span>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
