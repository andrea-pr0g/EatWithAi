import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Users, 
  Sparkles, 
  Bot, 
  CheckCircle2, 
  Compass, 
  Maximize2,
  Calendar,
  Radio,
  Clock
} from 'lucide-react';

export default function ZonesSection({ onSelectZone, onOpenWizard }) {
  const [activeZone, setActiveZone] = useState('indoor');
  const [tablesMap, setTablesMap] = useState({});
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    const fetchLiveTables = () => {
      fetch('/api/tables')
        .then(res => res.json())
        .then(data => {
          if (data && data.tables) {
            const map = {};
            data.tables.forEach(t => {
              map[t.name] = t;
            });
            setTablesMap(map);
            setLastSync(new Date().toLocaleTimeString());
          }
        })
        .catch(err => console.error("Could not fetch tables live:", err));
    };

    fetchLiveTables();
    const interval = setInterval(fetchLiveTables, 8000);
    return () => clearInterval(interval);
  }, []);

  const zones = [
    {
      id: 'indoor',
      name: 'Indoor Nebula Lounge',
      badge: 'Main Dining Room',
      capacity: '24 Seats • 6 Tables',
      tables: ['T01', 'T02', 'T03', 'T04', 'T05', 'T06'],
      combinations: 'T01 + T02 (up to 4) • T04 + T05 (up to 8)',
      description: 'The core orbital chamber featuring floor-to-ceiling curved observation windows, warm leather booths, and dynamic celestial ceiling lights.',
      atmosphere: 'Cozy, elegant, and atmospheric fine dining with planetary views.',
      idealFor: 'Couples, families, and dinner parties (1-8 guests).'
    },
    {
      id: 'terrace',
      name: 'Starlight Covered Terrace',
      badge: 'Observation Dome',
      capacity: '22 Seats • 5 Tables',
      tables: ['TR01', 'TR02', 'TR03', 'TR04', 'TR05'],
      combinations: 'TR01 + TR02 (up to 6) • TR03 + TR04 (up to 8)',
      description: 'An open-air pressurized glass dome with 360-degree unobstructed views of the Milky Way, star clusters, and solar auroras.',
      atmosphere: 'Romantic, breezy simulated micro-gravity atmosphere under open stars.',
      idealFor: 'Anniversaries, celebrations, and outdoor enthusiasts (1-8 guests).'
    },
    {
      id: 'bar',
      name: 'Meteorite Bar & High-Tops',
      badge: 'Cocktail & Soda Lounge',
      capacity: '6 Seats • 3 High-Tops',
      tables: ['B01', 'B02', 'B03'],
      combinations: 'Individual high-tops',
      description: 'A sleek black obsidian counter backlit with neon nebula blues. Serving hand-spun milkshakes, draft root beer floats, and artisan appetizers.',
      atmosphere: 'Casual, vibrant, and futuristic station bar vibe.',
      idealFor: 'Solo travelers, quick snacks, and drinks (1-2 guests).'
    },
    {
      id: 'private_room',
      name: 'Orbital Private Dining Suite',
      badge: 'VIP Sector',
      capacity: '16 Seats • 1 Grand Table',
      tables: ['P01 (Bespoke 16-seater)'],
      combinations: 'Exclusive private banquet facility',
      description: 'A fully secluded, sound-insulated orbital VIP salon with private holographic controls, dedicated service staff, and custom multi-course tasting setups.',
      atmosphere: 'Supreme exclusivity, private executive luxury, and customized lighting.',
      idealFor: 'Corporate summits, milestone birthdays, and private galas (8-16 guests).'
    }
  ];

  const current = zones.find(z => z.id === activeZone) || zones[0];

  return (
    <section id="zones" className="py-24 relative bg-cosmos-950 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 text-xs font-mono mb-4">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>4 UNIQUE CELESTIAL DINING ATMOSPHERES</span>
          </div>
          <h2 className="font-orbitron text-3xl sm:text-5xl font-extrabold text-white tracking-wide">
            Station <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">Dining Zones</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg mt-3">
            Choose your vantage point in orbit. Every zone is mapped and synchronized live with our PostgreSQL table allocation database.
          </p>
        </div>

        {/* Zone Selector Buttons */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
          {zones.map((zone) => (
            <button
              key={zone.id}
              onClick={() => setActiveZone(zone.id)}
              className={`p-4 rounded-2xl text-left transition-all duration-300 border ${
                activeZone === zone.id
                  ? 'glass-panel border-cyan-400 shadow-neon-cyan translate-y-[-2px]'
                  : 'bg-cosmos-900/60 border-white/10 hover:border-white/20 hover:bg-cosmos-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  activeZone === zone.id ? 'bg-cyan-500/20 text-cyan-300' : 'bg-cosmos-800 text-slate-400'
                }`}>
                  {zone.badge}
                </span>
                {activeZone === zone.id && (
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                )}
              </div>
              <h3 className="font-orbitron font-bold text-sm sm:text-base text-white">
                {zone.name}
              </h3>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                {zone.capacity}
              </p>
            </button>
          ))}
        </div>

        {/* Active Zone Detail Showcase Card */}
        <div className="glass-panel rounded-3xl p-6 sm:p-10 border border-white/15 shadow-cosmic-card">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Zone Info Column */}
            <div className="lg:col-span-7 space-y-6">
              <div>
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">
                  Zone Blueprint // {current.badge}
                </span>
                <h3 className="font-orbitron text-2xl sm:text-3xl font-bold text-white mt-1">
                  {current.name}
                </h3>
                <p className="text-slate-300 text-sm sm:text-base mt-3 leading-relaxed">
                  {current.description}
                </p>
              </div>

              {/* Atmosphere & Ideal For */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl glass-card">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Atmosphere</span>
                  <p className="text-xs text-slate-200">{current.atmosphere}</p>
                </div>
                <div className="p-4 rounded-xl glass-card">
                  <span className="text-xs font-mono text-slate-400 block mb-1">Recommended Party</span>
                  <p className="text-xs text-slate-200">{current.idealFor}</p>
                </div>
              </div>

              {/* Tables & Combinations from DB */}
              <div className="p-4 rounded-xl bg-cosmos-900/90 border border-white/10 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Database Assigned Tables:</span>
                  <span className="text-cyan-300 font-semibold">{current.tables.join(', ')}</span>
                </div>
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Joined Table Logic:</span>
                  <span className="text-violet-300">{current.combinations}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={() => onSelectZone(current.name)}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-medium text-sm flex items-center gap-2 shadow-neon-cyan transition-all"
                >
                  <Bot className="w-4 h-4" />
                  <span>Ask AI Host for {current.name}</span>
                </button>
                <button
                  onClick={onOpenWizard}
                  className="px-6 py-3 rounded-xl glass-card hover:bg-white/10 text-slate-200 text-sm font-medium border border-white/10 flex items-center gap-2 transition-all"
                >
                  <Calendar className="w-4 h-4 text-cyan-400" />
                  <span>Reserve Table Here</span>
                </button>
              </div>

            </div>

            {/* Visual Zone Schematic Preview */}
            <div className="lg:col-span-5">
              <div className="p-6 rounded-2xl bg-cosmos-900/90 border border-cyan-500/30 relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                  <span className="text-xs font-mono text-cyan-400 flex items-center gap-2">
                    <Compass className="w-4 h-4" />
                    LIVE STATION ALLOCATION MAP
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/30">
                      LIVE DB SYNC {lastSync ? `• ${lastSync}` : 'ACTIVE'}
                    </span>
                  </div>
                </div>

                {/* Table Layout Visualizer */}
                <div className="grid grid-cols-3 gap-3 py-4">
                  {current.tables.map((tbl, idx) => {
                    const rawName = tbl.split(' ')[0];
                    const tData = tablesMap[rawName];
                    const isOccupied = tData && tData.available === false && tData.active === true;
                    const isInactive = tData && tData.active === false;

                    return (
                      <div 
                        key={idx}
                        className={`p-3 sm:p-4 rounded-xl border text-center transition-all group cursor-pointer ${
                          isOccupied 
                            ? 'bg-rose-950/40 border-rose-500/40 hover:border-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.15)]' 
                            : isInactive
                            ? 'bg-slate-900/40 border-slate-700/40 opacity-60'
                            : 'bg-cosmos-800/80 border-emerald-500/30 hover:border-emerald-400 hover:shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                        }`}
                      >
                        <div className={`w-8 h-8 rounded-lg font-mono text-xs flex items-center justify-center mx-auto mb-2 transition-colors ${
                          isOccupied
                            ? 'bg-rose-900/60 border border-rose-500/60 text-rose-300 group-hover:bg-rose-500 group-hover:text-cosmos-950'
                            : isInactive
                            ? 'bg-slate-800 border border-slate-600 text-slate-400'
                            : 'bg-emerald-950 border border-emerald-500/40 text-emerald-300 group-hover:bg-emerald-500 group-hover:text-cosmos-950'
                        }`}>
                          {rawName}
                        </div>
                        <div className="text-[11px] font-mono text-slate-200 font-medium">{tbl}</div>
                        
                        {/* Occupancy Status Badge */}
                        <div className="mt-1">
                          {isOccupied ? (
                            <span className="inline-flex items-center gap-1 text-[9px] font-mono font-semibold text-rose-400">
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse"></span>
                              Occupied
                            </span>
                          ) : isInactive ? (
                            <span className="text-[9px] font-mono text-slate-400">
                              Maintenance
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[9px] font-mono font-semibold text-emerald-400">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                              Available
                            </span>
                          )}
                        </div>

                        {/* Guest / Remaining info if occupied */}
                        {isOccupied && tData?.customer_name && (
                          <div className="text-[8px] font-mono text-rose-300/80 mt-1 truncate" title={tData.customer_name}>
                            {tData.customer_name}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="text-[11px] text-slate-400 font-mono border-t border-white/10 pt-3 flex items-center justify-between">
                  <span>Continuous Occupancy Guard Active</span>
                  <span className="text-cyan-400">DB available Column Synced</span>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}
