"use client";
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, User, Phone, Mail, CheckCircle2, CreditCard } from 'lucide-react';

import { API_URL as API } from '../api';

interface RazorpayOrder {
  key_id: string;
  amount: number;
  currency: string;
  order_id: string;
}

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  order_id: string;
  name: string;
  description: string;
  handler: () => void;
  prefill: { name: string; contact: string; email: string };
  theme: { color: string };
}

interface RazorpayInstance {
  open: () => void;
}

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

export default function BookingForm() {
  const [services, setServices] = useState<{id: number, name: string, price: number, duration_minutes: number}[]>([]);
  const [form, setForm] = useState({ name: '', phone: '', email: '', serviceId: '', date: '' });
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'paying' | 'paid'>('idle');
  const [bookingId, setBookingId] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetch(`${API}/services/`)
      .then(r => r.json())
      .then(data => {
        if (data.services) {
          setServices(data.services);
        } else {
          setServices(data);
        }
      })
      .catch((e) => console.log('Failed to fetch services', e));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.phone || !form.serviceId || !form.date) return;
    setStatus('submitting');
    setErrorMsg('');

    try {
      const response = await fetch(`${API}/bookings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: parseInt(form.serviceId),
          customer_name: form.name,
          customer_phone: form.phone,
          customer_email: form.email || '',
          appointment_time: new Date(form.date).toISOString(),
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setBookingId(data.id);
        setStatus('success');
      } else {
        const err = await response.json();
        setErrorMsg(err.detail || 'Booking failed');
        setStatus('idle');
      }
    } catch {
      setErrorMsg('Server unreachable');
      setStatus('idle');
    }
  };

  const handlePayment = async () => {
    if (!bookingId) return;
    const svc = services.find(s => s.id === parseInt(form.serviceId));
    if (!svc) return;

    setStatus('paying');
    try {
      const res = await fetch(`${API}/payments/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_id: bookingId,
          amount: svc.price,
          customer_name: form.name,
          customer_email: form.email,
          customer_phone: form.phone,
        }),
      });
      if (res.ok) {
        const order = await res.json();
        // If Razorpay JS is loaded, open checkout
        if (typeof window !== 'undefined' && window.Razorpay) {
          const typedOrder = order as RazorpayOrder;
          const rzp = new window.Razorpay({
            key: typedOrder.key_id,
            amount: typedOrder.amount,
            currency: typedOrder.currency,
            order_id: typedOrder.order_id,
            name: 'BookSmart AI',
            description: svc.name,
            handler: () => setStatus('paid'),
            prefill: { name: form.name, contact: form.phone, email: form.email },
            theme: { color: '#2C3E35' },
          });
          rzp.open();
        } else {
          // Demo mode — simulate payment
          setTimeout(() => setStatus('paid'), 1000);
        }
      }
    } catch {
      setStatus('success'); // fallback
    }
  };

  const selectedPrice = services.length > 0 ? services.find(s => s.id === parseInt(form.serviceId))?.price : null;

  // Helper functions to avoid type assertions
  const shouldShowPayment = status === 'success' && selectedPrice != null;
  const isPaymentProcessing = status === 'paying';

  return (
    <section id="book" className="py-24 bg-[#FAF9F6] px-6 lg:px-12">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="bg-white rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col md:flex-row border border-gray-100"
        >
          <div className="bg-[#2C3E35] text-white p-12 md:w-5/12 flex flex-col justify-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#4A6B53] rounded-full blur-3xl opacity-50 -translate-y-1/2 translate-x-1/2"></div>
            <h3 className="text-4xl font-serif mb-6 relative z-10">Reserve Your <br/>Experience</h3>
            <p className="opacity-80 leading-relaxed mb-10 relative z-10 font-medium">
              Select your desired service and time. Our system will instantly map your schedule and dispatch a booking confirmation to your mobile device and email.
            </p>
            <div className="space-y-6 relative z-10 text-sm font-medium">
              <div className="flex flex-col"><span className="opacity-50 text-[10px] uppercase tracking-widest font-bold mb-1">Flagship Studio</span><span className="text-lg">South Ex, New Delhi</span></div>
              <div className="flex flex-col"><span className="opacity-50 text-[10px] uppercase tracking-widest font-bold mb-1">Working Hours</span><span className="text-lg">9:00 AM - 8:00 PM</span></div>
            </div>
          </div>

          <div className="p-12 md:w-7/12 bg-white">
            {status === 'paid' ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-10">
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                  className="w-24 h-24 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-6 shadow-sm border border-emerald-100">
                  <CreditCard className="w-12 h-12" />
                </motion.div>
                <h3 className="text-3xl font-serif text-[#1A2520] mb-4">Payment Complete!</h3>
                <p className="text-gray-500 font-medium text-lg max-w-sm">Your booking is confirmed and paid. See you soon!</p>
                <button 
                  key="reset-paid"
                  onClick={() => { setForm({name:'',phone:'',email:'',serviceId:'',date:''}); setStatus('idle'); setBookingId(null); }}
                  className="mt-10 px-8 py-3 bg-gray-50 text-[#4A6B53] rounded-full font-bold hover:bg-gray-100 transition border border-gray-200 shadow-sm"
                >
                  Book another session
                </button>
              </div>
            ) : status === 'success' ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-10">
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                  className="w-24 h-24 bg-green-50 text-green-600 rounded-full flex items-center justify-center mb-6 shadow-sm border border-green-100">
                  <CheckCircle2 className="w-12 h-12" />
                </motion.div>
                <h3 className="text-3xl font-serif text-[#1A2520] mb-4">Booking Confirmed!</h3>
                <p className="text-gray-500 font-medium text-lg max-w-sm">We&apos;ve securely reserved your slot. Confirmation sent via SMS{form.email ? ' & email' : ''}.</p>

                {shouldShowPayment && (
                  <button 
                    key="payment-btn"
                    onClick={handlePayment} 
                    disabled={isPaymentProcessing}
                    className="mt-8 px-8 py-4 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-xl flex items-center gap-2 disabled:opacity-70"
                  >
                    <CreditCard className="w-5 h-5" />
                    {isPaymentProcessing ? 'Processing…' : `Pay ₹${selectedPrice} Online`}
                  </button>
                )}
                <button 
                  key="skip-payment-btn"
                  onClick={() => { setForm({name:'',phone:'',email:'',serviceId:'',date:''}); setStatus('idle'); setBookingId(null); }}
                  className="mt-4 px-8 py-3 bg-gray-50 text-[#4A6B53] rounded-full font-bold hover:bg-gray-100 transition border border-gray-200 shadow-sm text-sm"
                >
                  Skip payment & book another
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                {errorMsg && (
                  <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm font-semibold border border-red-100">{errorMsg}</div>
                )}
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider text-[11px]">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                    <input type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                      className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#4A6B53] focus:border-transparent outline-none transition font-medium" placeholder="Priya Sharma" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider text-[11px]">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                      <input type="tel" required value={form.phone} onChange={e => setForm({...form, phone: e.target.value})}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#4A6B53] focus:border-transparent outline-none transition font-medium" placeholder="+91 98765 43210" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider text-[11px]">Email (Optional)</label>
                    <div className="relative">
                      <Mail className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                      <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#4A6B53] focus:border-transparent outline-none transition font-medium" placeholder="priya@email.com" />
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider text-[11px]">Service Type</label>
                    <select required value={form.serviceId} onChange={e => setForm({...form, serviceId: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#4A6B53] focus:border-transparent outline-none transition appearance-none font-medium text-gray-700">
                      <option value="" disabled>Select from catalog</option>
                      {services && services.length > 0 ? services.map(s => <option key={s.id} value={s.id}>{s.name} (₹{s.price})</option>) : <option value="" disabled>Select from catalog</option>}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider text-[11px]">Date & Time</label>
                    <div className="relative">
                      <Calendar className="absolute left-4 top-3.5 w-5 h-5 text-gray-400 pointer-events-none" />
                      <input type="datetime-local" required value={form.date} onChange={e => setForm({...form, date: e.target.value})}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#4A6B53] focus:border-transparent outline-none transition font-medium" />
                    </div>
                  </div>
                </div>
                <button 
                  key="submit-btn"
                  disabled={status === 'submitting'} 
                  type="submit"
                  className="w-full py-4 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition hover:shadow-lg disabled:opacity-70 mt-4 shadow-md shadow-gray-200"
                >
                  {status === 'submitting' ? 'Checking availability…' : 'Confirm Reservation'}
                </button>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
