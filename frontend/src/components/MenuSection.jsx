import React, { useState, useEffect } from 'react';
import { 
  UtensilsCrossed, 
  Flame, 
  Leaf, 
  Wheat, 
  Search, 
  Sparkles, 
  Bot, 
  DollarSign, 
  HeartHandshake,
  Check,
  ChevronRight
} from 'lucide-react';

export default function MenuSection({ onAskAboutDish }) {
  const [categories, setCategories] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [dietaryFilter, setDietaryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // Fetch real menu from database API
  useEffect(() => {
    fetch('/api/menu')
      .then(res => res.json())
      .then(data => {
        if (data && data.items) {
          setCategories(data.available_categories || data.categories || []);
          setMenuItems(data.items || []);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch menu:', err);
        setLoading(false);
      });
  }, []);

  // Filter items
  const filteredItems = menuItems.filter(item => {
    // Category match
    if (selectedCategory !== 'all' && item.category_name !== selectedCategory) {
      return false;
    }
    // Dietary match
    if (dietaryFilter === 'vegetarian' && !item.is_vegetarian) return false;
    if (dietaryFilter === 'vegan' && !item.is_vegan) return false;
    if (dietaryFilter === 'gluten_free' && !item.is_gluten_free) return false;
    
    // Search query match
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const nameMatch = item.name.toLowerCase().includes(q);
      const descMatch = item.description?.toLowerCase().includes(q);
      const allergenMatch = item.allergens?.toLowerCase().includes(q);
      if (!nameMatch && !descMatch && !allergenMatch) return false;
    }
    return true;
  });

  return (
    <section id="menu" className="py-24 relative cosmic-stars">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-violet-950/70 border border-violet-500/40 text-violet-300 text-xs font-mono mb-4">
            <UtensilsCrossed className="w-3.5 h-3.5 text-violet-400" />
            <span>COSMIC GASTRONOMY • 35 DATABASE DISHES</span>
          </div>
          <h2 className="font-orbitron text-3xl sm:text-5xl font-extrabold text-white tracking-wide">
            Galactic <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400 bg-clip-text text-transparent">Dining Menu</span>
          </h2>
          <p className="text-slate-300 text-base sm:text-lg mt-4 leading-relaxed">
            Feast on USDA Prime steaks charbroiled over open coals, 14-hour post-oak smoked Texas BBQ, 
            and smash burgers crafted in low Earth orbit. All prepared fresh to order.
          </p>
        </div>

        {/* Featured Coherent Photography Showcase Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {/* Card 1: Handcrafted Burgers */}
          <div className="group relative rounded-2xl overflow-hidden glass-card border border-white/10 hover:border-cyan-500/40 transition-all duration-300 hover:shadow-neon-cyan">
            <div className="h-64 overflow-hidden relative">
              <img 
                src="/assets/american-burger.jpg" 
                alt="Handcrafted American Cheeseburger with signature garlic fries"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-cosmos-950 via-cosmos-950/30 to-transparent"></div>
              <span className="absolute top-4 left-4 text-xs font-mono px-3 py-1 rounded-full bg-cosmos-950/80 backdrop-blur-md text-cyan-300 border border-cyan-500/30">
                Half-Pound Angus Beef
              </span>
            </div>
            <div className="p-5">
              <h3 className="font-orbitron text-xl font-bold text-white group-hover:text-cyan-300 transition-colors">
                Handcrafted Smash Burgers
              </h3>
              <p className="text-sm text-slate-400 mt-2 line-clamp-2">
                Certified Angus beef smashed with sweet Vidalia onions, double melted Wisconsin cheddar, and applewood smoked bacon on toasted brioche.
              </p>
              <button 
                onClick={() => {
                  setSelectedCategory('Handcrafted Burgers');
                  onAskAboutDish("What handcrafted burgers do you recommend?");
                }}
                className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-cyan-400 hover:text-cyan-300"
              >
                <span>View 4 burger styles</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Card 2: USDA Prime Steaks */}
          <div className="group relative rounded-2xl overflow-hidden glass-card border border-white/10 hover:border-violet-500/40 transition-all duration-300 hover:shadow-neon-violet">
            <div className="h-64 overflow-hidden relative">
              <img 
                src="/assets/prime-ribeye.jpg" 
                alt="14 oz USDA Prime Ribeye Steak charbroiled with garlic herb butter"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-cosmos-950 via-cosmos-950/30 to-transparent"></div>
              <span className="absolute top-4 left-4 text-xs font-mono px-3 py-1 rounded-full bg-cosmos-950/80 backdrop-blur-md text-violet-300 border border-violet-500/30">
                USDA Prime Cuts
              </span>
            </div>
            <div className="p-5">
              <h3 className="font-orbitron text-xl font-bold text-white group-hover:text-violet-300 transition-colors">
                Steaks & Prime Cuts
              </h3>
              <p className="text-sm text-slate-400 mt-2 line-clamp-2">
                Hand-cut 14 oz Prime Ribeye, 8 oz Center-Cut Filet Mignon, and Kansas City bone-in strip, basted with roasted garlic herb butter.
              </p>
              <button 
                onClick={() => {
                  setSelectedCategory('Steaks & Prime Cuts');
                  onAskAboutDish("Tell me about the USDA Prime Ribeye and steaks");
                }}
                className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-violet-400 hover:text-violet-300"
              >
                <span>Explore Prime Cuts</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Card 3: Shakes & Floats */}
          <div className="group relative rounded-2xl overflow-hidden glass-card border border-white/10 hover:border-amber-500/40 transition-all duration-300 hover:shadow-neon-cyan">
            <div className="h-64 overflow-hidden relative">
              <img 
                src="/assets/rootbeer-shake.jpg" 
                alt="Draft Root Beer Float and Oreo Milkshake in cosmic space lounge"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-cosmos-950 via-cosmos-950/30 to-transparent"></div>
              <span className="absolute top-4 left-4 text-xs font-mono px-3 py-1 rounded-full bg-cosmos-950/80 backdrop-blur-md text-amber-300 border border-amber-500/30">
                Hand-Spun Creamery
              </span>
            </div>
            <div className="p-5">
              <h3 className="font-orbitron text-xl font-bold text-white group-hover:text-amber-300 transition-colors">
                Shakes & Old-Fashioned Floats
              </h3>
              <p className="text-sm text-slate-400 mt-2 line-clamp-2">
                Draft sarsaparilla root beer floats, thick Oreo cookies & cream milkshakes, and Madagascar vanilla bean shakes spun to perfection.
              </p>
              <button 
                onClick={() => {
                  setSelectedCategory('Beverages & Hand-Spun Shakes');
                  onAskAboutDish("What milkshakes and beverages do you have?");
                }}
                className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-amber-400 hover:text-amber-300"
              >
                <span>View all shakes & drinks</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Interactive Search & Filter Controls */}
        <div className="mb-10 p-5 rounded-2xl glass-panel border border-white/10 space-y-4">
          
          {/* Top row: Search and Dietary filters */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            
            {/* Search input */}
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search brisket, wings, burger, allergen..."
                className="w-full bg-cosmos-900/90 pl-10 pr-4 py-2.5 rounded-xl border border-white/15 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-400"
              />
            </div>

            {/* Dietary Toggle buttons */}
            <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
              <button
                onClick={() => setDietaryFilter('all')}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                  dietaryFilter === 'all'
                    ? 'bg-cyan-500 text-cosmos-950 font-bold'
                    : 'bg-cosmos-800 text-slate-300 hover:bg-cosmos-700'
                }`}
              >
                All Diets
              </button>
              <button
                onClick={() => setDietaryFilter('vegetarian')}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1 transition-all ${
                  dietaryFilter === 'vegetarian'
                    ? 'bg-emerald-500 text-cosmos-950 font-bold'
                    : 'bg-cosmos-800 text-slate-300 hover:bg-cosmos-700'
                }`}
              >
                <Leaf className="w-3 h-3 text-emerald-400" />
                Vegetarian
              </button>
              <button
                onClick={() => setDietaryFilter('vegan')}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1 transition-all ${
                  dietaryFilter === 'vegan'
                    ? 'bg-teal-500 text-cosmos-950 font-bold'
                    : 'bg-cosmos-800 text-slate-300 hover:bg-cosmos-700'
                }`}
              >
                <Leaf className="w-3 h-3 text-teal-300" />
                Vegan
              </button>
              <button
                onClick={() => setDietaryFilter('gluten_free')}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium flex items-center gap-1 transition-all ${
                  dietaryFilter === 'gluten_free'
                    ? 'bg-amber-500 text-cosmos-950 font-bold'
                    : 'bg-cosmos-800 text-slate-300 hover:bg-cosmos-700'
                }`}
              >
                <Wheat className="w-3 h-3 text-amber-300" />
                Gluten-Free
              </button>
            </div>

          </div>

          {/* Category Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pt-2 border-t border-white/5">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`text-xs font-mono uppercase px-4 py-2 rounded-xl whitespace-nowrap transition-all ${
                selectedCategory === 'all'
                  ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white font-bold shadow-neon-cyan'
                  : 'bg-cosmos-800/80 text-slate-400 hover:text-white hover:bg-cosmos-700'
              }`}
            >
              All Categories ({menuItems.length})
            </button>
            {categories.map((cat, idx) => {
              const catName = typeof cat === 'string' ? cat : cat.name;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedCategory(catName)}
                  className={`text-xs font-mono uppercase px-4 py-2 rounded-xl whitespace-nowrap transition-all ${
                    selectedCategory === catName
                      ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white font-bold shadow-neon-cyan'
                      : 'bg-cosmos-800/80 text-slate-400 hover:text-white hover:bg-cosmos-700'
                  }`}
                >
                  {catName}
                </button>
              );
            })}
          </div>

        </div>

        {/* Menu Items Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="w-10 h-10 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-sm font-mono text-cyan-300">Syncing menu from database...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-16 glass-card rounded-2xl">
            <p className="text-slate-400">No dishes match your selected filter or search term.</p>
            <button
              onClick={() => {
                setSelectedCategory('all');
                setDietaryFilter('all');
                setSearchQuery('');
              }}
              className="mt-4 px-4 py-2 text-xs font-mono text-cyan-400 border border-cyan-500/30 rounded-lg hover:bg-cyan-950/40"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map((item) => (
              <div 
                key={item.item_id} 
                className="glass-card rounded-2xl p-6 flex flex-col justify-between border border-white/5 hover:border-cyan-500/30 transition-all duration-300 hover:-translate-y-1 group"
              >
                <div>
                  {/* Category & Price Header */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider bg-cyan-950/60 px-2.5 py-0.5 rounded-full border border-cyan-800/40">
                      {item.category_name}
                    </span>
                    <span className="font-orbitron font-bold text-lg text-emerald-400">
                      ${Number(item.price).toFixed(2)}
                    </span>
                  </div>

                  {/* Dish Name */}
                  <h4 className="font-orbitron font-bold text-lg text-white group-hover:text-cyan-300 transition-colors">
                    {item.name}
                  </h4>

                  {/* Description */}
                  <p className="text-xs text-slate-300 mt-2.5 leading-relaxed font-light">
                    {item.description}
                  </p>
                </div>

                {/* Footer with Dietary Badges, Calories & AI Button */}
                <div className="mt-5 pt-4 border-t border-white/5 space-y-3">
                  <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-400">
                    {item.calories && (
                      <span className="bg-cosmos-800 px-2 py-0.5 rounded">
                        {item.calories} kcal
                      </span>
                    )}
                    {item.spicy_level > 0 && (
                      <span className="bg-red-950/70 text-red-300 px-2 py-0.5 rounded flex items-center gap-0.5 border border-red-800/30">
                        <Flame className="w-3 h-3 text-red-400 inline" />
                        {item.spicy_level === 1 ? 'Mild Spice' : 'Fiery Hot'}
                      </span>
                    )}
                    {item.is_vegetarian && (
                      <span className="bg-emerald-950/70 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800/30">
                        Vegetarian
                      </span>
                    )}
                    {item.is_vegan && (
                      <span className="bg-teal-950/70 text-teal-300 px-2 py-0.5 rounded border border-teal-800/30">
                        Vegan
                      </span>
                    )}
                    {item.is_gluten_free && (
                      <span className="bg-amber-950/70 text-amber-300 px-2 py-0.5 rounded border border-amber-800/30">
                        Gluten-Free
                      </span>
                    )}
                  </div>

                  {/* Ask AI Host Button */}
                  <button
                    onClick={() => onAskAboutDish(`Tell me more about the "${item.name}" and what side dishes or pairings you recommend with it.`)}
                    className="w-full py-2 px-3 rounded-xl bg-cosmos-800/80 hover:bg-cyan-950 text-slate-300 hover:text-cyan-300 border border-white/10 hover:border-cyan-500/30 text-xs font-mono flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Bot className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Ask AI Host About This Dish</span>
                  </button>
                </div>

              </div>
            ))}
          </div>
        )}

      </div>
    </section>
  );
}
