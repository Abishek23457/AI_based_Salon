"use client";
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

import { API_URL as API } from '../api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', salon_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const url = isRegister ? `${API}/auth/register` : `${API}/auth/login`;
    const body = isRegister
      ? { username: form.username, password: form.password, salon_name: form.salon_name }
      : { username: form.username, password: form.password };

    console.log('Attempting to login...');

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      console.log('Response status:', res.status);
      console.log('Response ok:', res.ok);

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('booksmart_token', data.access_token);
        localStorage.setItem('booksmart_salon_id', data.salon_id.toString());
        localStorage.setItem('booksmart_user', data.username);
        console.log('Login successful:', data);
        navigate('/dashboard');
      } else {
        const err = await res.json();
        console.error('Login failed:', err);
        setError(err.detail || 'Something went wrong');
      }
    } catch (err) {
      console.error('Network error:', err);
      setError('Cannot reach the server. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  // Test default credentials
  const testLogin = async () => {
    setForm({ username: 'admin', password: 'admin123', salon_name: '' });
    setIsRegister(false);
  };

  return (
    <div className="min-h-screen bg-[#E9EFE6] flex items-center justify-center px-4 font-sans">
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row max-w-4xl w-full border border-gray-100"
      >
        {/* Left Panel */}
        <div className="bg-[#1A2520] text-white p-12 md:w-5/12 flex flex-col justify-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-72 h-72 bg-[#4A6B53] rounded-full blur-3xl opacity-40 -translate-y-1/2 translate-x-1/2" />
          <h1 className="text-4xl font-serif mb-4 relative z-10">BookSmart<br/>AI</h1>
          <p className="opacity-60 leading-relaxed relative z-10 text-sm font-medium">
            Your AI-powered salon management platform. Manage bookings, train your digital receptionist,
            and grow your business — all from one dashboard.
          </p>
          <div className="mt-10 relative z-10 space-y-4 text-xs font-medium text-white/40">
            <div>✦ AI-powered voice & chat receptionist</div>
            <div>✦ Real-time booking analytics</div>
            <div>✦ Razorpay payment integration</div>
          </div>
        </div>

        {/* Right Panel — Form */}
        <div className="p-12 md:w-7/12">
          <h2 className="text-2xl font-bold text-[#1A2520] mb-1">{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
          <p className="text-gray-400 font-medium text-sm mb-8">{isRegister ? 'Set up your salon in 30 seconds' : 'Log in to your dashboard'}</p>

          {error && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm font-semibold mb-6 border border-red-100">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Username</label>
              <input required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium"
                placeholder="admin" />
            </div>
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Password</label>
              <input required type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium"
                placeholder="••••••••" />
            </div>
            {isRegister && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}>
                <label className="block text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Salon Name</label>
                <input required value={form.salon_name} onChange={e => setForm({ ...form, salon_name: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium"
                  placeholder="My Awesome Salon" />
              </motion.div>
            )}
            <button type="submit" disabled={loading}
              className="w-full py-4 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-md disabled:opacity-70 mt-2">
              {loading ? 'Please wait…' : isRegister ? 'Create Account & Salon' : 'Log In'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-400 font-medium">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
            <button onClick={() => { setIsRegister(!isRegister); setError(''); }}
              className="text-[#4A6B53] font-bold ml-1 hover:underline">
              {isRegister ? 'Log in' : 'Register'}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
