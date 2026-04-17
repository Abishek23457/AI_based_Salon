import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, List, LayoutGrid, X, ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, string> = {
    confirmed: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-600',
    completed: 'bg-blue-100 text-blue-600',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase ${cfg[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
}

export default function AppointmentsTab({ bookings, services, viewMode, setViewMode, cancelBooking, currentMonth, setCurrentMonth }: any) {
  
  const serviceName = (id: number) => services.find((s: any) => s.id === id)?.name ?? `Service #${id}`;

  const renderCalendarDays = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart, { weekStartsOn: 1 });
    const endDate = endOfWeek(monthEnd, { weekStartsOn: 1 });

    const dateFormat = "d";
    const rows: React.ReactNode[] = [];
    let days: React.ReactNode[] = [];

    const daysInterval = eachDayOfInterval({ start: startDate, end: endDate });

    daysInterval.forEach((d, i) => {
      const formattedDate = format(d, dateFormat);
      const isCurrentMonth = isSameMonth(d, monthStart);
      const dayBookings = bookings.filter((b: any) => isSameDay(new Date(b.appointment_time), d) && b.status !== 'cancelled');

      days.push(
        <div key={d.toString()} className={`min-h-[100px] border border-gray-100 p-2 transition-all ${isCurrentMonth ? 'bg-white' : 'bg-gray-50 text-gray-300'}`}>
          <div className="flex justify-end mb-2">
            <span className={`text-sm font-bold w-6 h-6 flex items-center justify-center rounded-full ${isSameDay(d, new Date()) ? 'bg-[#2C3E35] text-white' : 'text-gray-500'}`}>
              {formattedDate}
            </span>
          </div>
          <div className="flex flex-col gap-1 overflow-y-auto max-h-20 no-scrollbar">
            {dayBookings.map((b: any) => (
              <div key={b.id} className="text-[10px] leading-tight px-2 py-1 bg-emerald-50 text-emerald-800 rounded font-medium truncate" title={`${b.customer_name} - ${serviceName(b.service_id)}`}>
                {format(new Date(b.appointment_time), 'HH:mm')} • {b.customer_name}
              </div>
            ))}
          </div>
        </div>
      );

      if ((i + 1) % 7 === 0) {
        rows.push(<div key={`row-${i}`} className="grid grid-cols-7">{days}</div>);
        days = [];
      }
    });

    return <div>{rows}</div>;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-bold text-[#1A2520] font-serif">Appointments</h1>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-1 flex items-center gap-1">
          <button onClick={() => setViewMode('list')} className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition ${viewMode === 'list' ? 'bg-[#2C3E35] text-white' : 'text-gray-500 hover:text-gray-800'}`}>
            <List className="w-4 h-4" /> List
          </button>
          <button onClick={() => setViewMode('calendar')} className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition ${viewMode === 'calendar' ? 'bg-[#2C3E35] text-white' : 'text-gray-500 hover:text-gray-800'}`}>
            <LayoutGrid className="w-4 h-4" /> Calendar
          </button>
        </div>
      </div>

      {viewMode === 'list' ? (
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['Customer', 'Contact', 'Service', 'Date & Time', 'Status', 'Action'].map(h => (
                  <th key={h} className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-gray-400">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bookings.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-16 text-gray-400 font-medium">No bookings found.</td></tr>
              ) : bookings.map((b: any) => (
                <tr key={b.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50/60 transition group">
                  <td className="px-6 py-4 font-bold text-[#2C3E35]">{b.customer_name}</td>
                  <td className="px-6 py-4 text-gray-500 text-xs">
                    {b.customer_phone} <br/><span className="text-gray-400">{b.customer_email}</span>
                  </td>
                  <td className="px-6 py-4 font-medium">{serviceName(b.service_id)}</td>
                  <td className="px-6 py-4 text-gray-500 font-mono text-xs">
                    {new Date(b.appointment_time).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                  </td>
                  <td className="px-6 py-4"><StatusBadge status={b.status} /></td>
                  <td className="px-6 py-4">
                    {b.status === 'confirmed' && (
                      <button onClick={() => cancelBooking(b.id)}
                        className="text-red-400 hover:text-red-600 transition text-xs font-bold flex items-center gap-1 opacity-0 group-hover:opacity-100">
                        <X className="w-3 h-3" /> Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden p-6">
          <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-2xl font-bold text-[#1A2520]">{format(currentMonth, 'MMMM yyyy')}</h2>
            <div className="flex gap-2">
              <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))} className="p-2 rounded-full hover:bg-gray-100"><ChevronLeft className="w-5 h-5"/></button>
              <button onClick={() => setCurrentMonth(new Date())} className="px-4 py-2 text-sm font-bold rounded-full hover:bg-gray-100">Today</button>
              <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="p-2 rounded-full hover:bg-gray-100"><ChevronRight className="w-5 h-5"/></button>
            </div>
          </div>
          <div className="grid grid-cols-7 mb-2">
             {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d => (
              <div key={d} className="text-center font-bold text-[10px] uppercase tracking-widest text-gray-400 py-2">{d}</div>
            ))}
          </div>
          <div className="border-l border-t border-gray-100 rounded-xl overflow-hidden">
            {renderCalendarDays()}
          </div>
        </div>
      )}
    </div>
  );
}
