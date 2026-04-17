import React from 'react';
import { TrendingUp, Users, Calendar, Clock, ArrowUpRight } from 'lucide-react';

export default function AnalyticsTab({ bookings, services }: any) {
  const totalRevenue = bookings
    .filter((b: any) => b.status === 'completed' || b.status === 'confirmed')
    .reduce((sum: number, b: any) => {
      const svc = services.find((s: any) => s.id === b.service_id);
      return sum + (svc?.price || 0);
    }, 0);

  const stats = [
    { label: 'Total Revenue', value: `₹${totalRevenue.toLocaleString()}`, icon: TrendingUp, color: 'emerald' },
    { label: 'Total Bookings', value: bookings.length, icon: Calendar, color: 'blue' },
    { label: 'Completion Rate', value: `${bookings.length > 0 ? Math.round((bookings.filter((b: any) => b.status === 'completed').length / bookings.length) * 100) : 0}%`, icon: Clock, color: 'teal' },
    { label: 'Active Clients', value: new Set(bookings.map((b: any) => b.customer_phone)).size, icon: Users, color: 'amber' },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-[#1A2520] font-serif">Business Insights</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 relative overflow-hidden group hover:shadow-md transition-shadow">
            <div className={`absolute top-0 right-0 w-24 h-24 -mr-8 -mt-8 rounded-full bg-${s.color}-50 transition-transform group-hover:scale-110`} />
            <div className="relative z-10">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-4 bg-${s.color}-100 text-${s.color}-600`}>
                <s.icon className="w-6 h-6" />
              </div>
              <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">{s.label}</p>
              <h3 className="text-2xl font-bold text-[#1A2520]">{s.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <h3 className="text-xl font-bold text-[#1A2520] font-serif mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {bookings.slice(0, 5).map((b: any) => (
              <div key={b.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-2xl">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center font-bold text-emerald-600 shadow-sm">
                    {b.customer_name[0]}
                  </div>
                  <div>
                    <p className="font-bold text-sm text-[#2C3E35]">{b.customer_name}</p>
                    <p className="text-[10px] text-gray-400 uppercase tracking-widest">{new Date(b.appointment_time).toLocaleDateString()}</p>
                  </div>
                </div>
                <ArrowUpRight className="w-4 h-4 text-gray-300" />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#2C3E35] rounded-3xl p-8 shadow-xl text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full -mr-32 -mt-32 blur-3xl" />
            <h3 className="text-xl font-bold font-serif mb-4 relative z-10">AI Performance</h3>
            <p className="text-emerald-100/60 text-sm mb-8 relative z-10">Review how the AI handles your calls and bookings.</p>
            <div className="space-y-6 relative z-10">
                <div className="flex justify-between items-end border-b border-white/10 pb-4">
                    <span className="text-xs font-bold uppercase tracking-widest opacity-60">Success Rate</span>
                    <span className="text-2xl font-bold">94%</span>
                </div>
                <div className="flex justify-between items-end border-b border-white/10 pb-4">
                    <span className="text-xs font-bold uppercase tracking-widest opacity-60">Avg. Call Time</span>
                    <span className="text-2xl font-bold">1:45</span>
                </div>
                <div className="flex justify-between items-end border-b border-white/10 pb-4">
                    <span className="text-xs font-bold uppercase tracking-widest opacity-60">Direct Revenue</span>
                    <span className="text-2xl font-bold">₹14,500</span>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
