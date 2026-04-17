import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart2, Users, Calendar, Settings, LogOut, Sparkles, 
  Search, Bell, Menu, X, Phone, Clock, MessageSquare, Briefcase
} from 'lucide-react';
import { API_URL as API } from '../api';

// Modular Tab Components
import AppointmentsTab from '../components/dashboard/AppointmentsTab';
import ServicesTab from '../components/dashboard/ServicesTab';
import StaffTab from '../components/dashboard/StaffTab';
import AnalyticsTab from '../components/dashboard/AnalyticsTab';
import AITab from '../components/dashboard/AITab';

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('bookings');
  const [salon, setSalon] = useState<any>(null);
  const [bookings, setBookings] = useState<any[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [toast, setToast] = useState('');
  const [svcForm, setSvcForm] = useState({ name: '', price: '', duration_minutes: '', description: '' });
  const [searchQuery, setSearchQuery] = useState('');

  const salonId = localStorage.getItem('booksmart_salon_id') || '1';
  const token = localStorage.getItem('booksmart_token');

  const authFetch = useCallback((url: string, options: any = {}) => {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }, [token]);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const loadData = useCallback(async () => {
    try {
      const [salonRes, bookingsRes, servicesRes] = await Promise.all([
        authFetch(`${API}/auth/me`),
        authFetch(`${API}/bookings/?salon_id=${salonId}`),
        authFetch(`${API}/services/?salon_id=${salonId}`)
      ]);

      if (!salonRes.ok) { navigate('/login'); return; }

      const [salonData, bookingsData, servicesData] = await Promise.all([
        salonRes.json(),
        bookingsRes.json(),
        servicesRes.json()
      ]);

      setSalon(salonData);
      setBookings(bookingsData);
      setServices(servicesData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, [authFetch, navigate]);

  useEffect(() => {
    if (!token) navigate('/login');
    else loadData();
  }, [token, navigate, loadData]);

  const addService = async (e: React.FormEvent, staffIds: number[] = []) => {
    e.preventDefault();
    const res = await authFetch(`${API}/services/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...svcForm, salon_id: parseInt(salonId), staff_ids: staffIds })
    });
    if (res.ok) {
      showToast('Service added ✓');
      setSvcForm({ name: '', price: '', duration_minutes: '', description: '' });
      loadData();
    } else {
      showToast('Failed to add service');
    }
  };

  const deleteService = async (id: number) => {
    if (!confirm('Remove this service?')) return;
    const res = await authFetch(`${API}/services/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Service removed');
      loadData();
    }
  };

  const cancelBooking = async (id: number) => {
    if (!confirm('Cancel this booking?')) return;
    const res = await authFetch(`${API}/bookings/${id}/cancel`, { method: 'PATCH' });
    if (res.ok) {
      showToast('Booking cancelled');
      loadData();
    }
  };

  const navItems = [
    { id: 'bookings', label: 'Appointments', icon: Calendar },
    { id: 'services', label: 'Services', icon: Briefcase },
    { id: 'staff', label: 'Staff Management', icon: Phone }, 
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'ai', label: 'Automation Hub', icon: Sparkles },
  ];

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#FAF9F6] text-[#4A6B53] font-bold animate-pulse">Initializing Admin Hub...</div>;

  return (
    <div className="flex min-h-screen bg-[#FAF9F6]">
      {/* Sidebar */}
      <aside className="w-72 bg-[#1A2520] text-emerald-50 hidden lg:flex flex-col p-8 fixed h-full shadow-2xl">
        <div className="flex items-center gap-4 mb-12 px-4 py-6 bg-white/5 rounded-[2rem] border border-white/5">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-serif text-lg font-bold">BookSmart</span>
            <span className="text-[10px] uppercase tracking-widest opacity-50 font-black">Admin Hub</span>
          </div>
        </div>

        <nav className="space-y-3 flex-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all duration-300 group
                ${activeTab === item.id ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'hover:bg-white/5 text-emerald-100/60'}`}
            >
              <item.icon className={`w-5 h-5 ${activeTab === item.id ? 'scale-110' : 'group-hover:scale-110 transition'}`} />
              <span className="text-sm font-bold tracking-tight">{item.label}</span>
            </button>
          ))}
        </nav>

        <button 
          onClick={() => { localStorage.clear(); navigate('/login'); }}
          className="mt-auto flex items-center gap-4 px-6 py-4 rounded-2xl hover:bg-red-500/10 text-red-300 transition group"
        >
          <LogOut className="w-5 h-5 group-hover:rotate-12 transition" />
          <span className="text-sm font-bold">Sign Out</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 lg:ml-72 p-10 lg:p-16">
        <header className="flex justify-between items-center mb-12">
           <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-[#2C3E35] rounded-full flex items-center justify-center text-white font-bold">{salon?.username?.[0].toUpperCase()}</div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Welcome back,</p>
                <h2 className="text-xl font-bold text-[#1A2520]">{salon?.salon_name}</h2>
              </div>
           </div>
           <div className="flex gap-4">
              <div className="w-48 bg-white border border-gray-100 rounded-full px-4 py-2 hidden md:flex items-center gap-2 shadow-sm">
                <Search className="w-4 h-4 text-gray-300" />
                <input 
                  placeholder="Quick search..." 
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="text-xs bg-transparent outline-none w-full font-medium" 
                />
              </div>
              <button className="relative p-3 bg-white border border-gray-100 rounded-full shadow-sm hover:bg-gray-50 transition">
                <Bell className="w-5 h-5 text-[#2C3E35]" />
                <span className="absolute top-3 right-3 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
              </button>
           </div>
        </header>

        {/* Dynamic Tab Rendering */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'bookings' && (
              <AppointmentsTab 
                bookings={bookings} 
                services={services} 
                viewMode={viewMode} 
                setViewMode={setViewMode} 
                cancelBooking={cancelBooking} 
                currentMonth={currentMonth} 
                setCurrentMonth={setCurrentMonth} 
              />
            )}
            
            {activeTab === 'services' && (
              <ServicesTab 
                services={services} 
                svcForm={svcForm} 
                setSvcForm={setSvcForm} 
                addService={addService} 
                deleteService={deleteService} 
                salonId={salonId}
                authFetch={authFetch}
                showToast={showToast}
              />
            )}

            {activeTab === 'staff' && (
              <StaffTab 
                salonId={salonId} 
                authFetch={authFetch} 
                showToast={showToast} 
              />
            )}

            {activeTab === 'analytics' && (
              <AnalyticsTab 
                bookings={bookings} 
                services={services} 
              />
            )}

            {activeTab === 'ai' && (
              <AITab 
                authFetch={authFetch} 
                showToast={showToast} 
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="fixed bottom-10 left-1/2 -translate-x-1/2 bg-[#2C3E35] text-white px-8 py-4 rounded-full shadow-2xl z-[200] font-bold text-sm border border-white/10"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
