"use client";
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Star, CheckCircle2 } from 'lucide-react';

import { API_URL as API } from '../api';

export default function ReviewPage() {
  const [form, setForm] = useState({ booking_id: '', customer_name: '', rating: 5, comment: '' });
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMsg('');

    try {
      const res = await fetch(`${API}/reviews/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_id: parseInt(form.booking_id),
          customer_name: form.customer_name,
          rating: form.rating,
          comment: form.comment
        }),
      });

      if (res.ok) {
        setStatus('success');
      } else {
        const data = await res.json();
        setErrorMsg(data.detail || 'Failed to submit review');
        setStatus('error');
      }
    } catch {
      setErrorMsg('Network error. Could not reach server.');
      setStatus('error');
    }
  };

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-[#E9EFE6] flex items-center justify-center p-6">
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-white rounded-3xl p-10 max-w-md w-full text-center shadow-xl border border-gray-100">
          <div className="w-20 h-20 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h2 className="text-3xl font-serif font-bold text-[#1A2520] mb-3">Thank You!</h2>
          <p className="text-gray-500 font-medium mb-8">Your feedback helps us provide a better experience for everyone.</p>
          <button onClick={() => setStatus('idle')} className="text-[#4A6B53] font-bold hover:underline">Submit another review</button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#E9EFE6] flex items-center justify-center p-6 font-sans">
      <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-white rounded-3xl shadow-xl max-w-md w-full overflow-hidden border border-gray-100">
        <div className="bg-[#1A2520] p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#4A6B53] rounded-full blur-2xl opacity-40 -translate-y-1/2 translate-x-1/2" />
          <h1 className="text-3xl font-serif text-white font-bold relative z-10">Rate Your Experience</h1>
          <p className="text-white/60 text-sm mt-2 font-medium relative z-10">We&apos;d love to hear about your recent salon visit.</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          {status === 'error' && <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm font-bold border border-red-100">{errorMsg}</div>}
          
          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Booking ID</label>
            <input required type="number" value={form.booking_id} onChange={e => setForm({...form, booking_id: e.target.value})} 
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" placeholder="e.g. 12" />
            <p className="text-[10px] text-gray-400 mt-1 pl-1">Found in your SMS/Email confirmation</p>
          </div>
          
          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Your Name</label>
            <input required value={form.customer_name} onChange={e => setForm({...form, customer_name: e.target.value})} 
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" placeholder="John Doe" />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Rating</label>
            <div className="flex gap-2 justify-center">
              {[1, 2, 3, 4, 5].map(star => (
                <button type="button" key={star} onClick={() => setForm({...form, rating: star})}
                  className={`p-2 rounded-full transition-all hover:scale-110 ${form.rating >= star ? 'text-amber-400 drop-shadow-sm' : 'text-gray-200'}`}>
                  <Star className={`w-10 h-10 ${form.rating >= star ? 'fill-current' : ''}`} />
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Feedback (Optional)</label>
            <textarea rows={3} value={form.comment} onChange={e => setForm({...form, comment: e.target.value})} 
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium resize-none" placeholder="Tell us what you liked..." />
          </div>

          <button type="submit" disabled={status === 'submitting'} 
            className="w-full py-4 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-md disabled:opacity-70 mt-2">
            {status === 'submitting' ? 'Submitting...' : 'Submit Review'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
