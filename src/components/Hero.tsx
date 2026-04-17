"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { PhoneCall, CalendarCheck, ArrowRight, Zap, Shield, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

// Client-only particles component
function ClientOnlyParticles() {
  const particles: Array<{
    id: number;
    left: number;
    top: number;
    x: [number, number];
    y: [number, number];
    duration: number;
    delay: number;
  }> = Array.from({ length: 20 }, (_, i) => {
    const left = (i * 17) % 100;
    const top = (i * 29) % 100;
    return {
      id: i,
      left,
      top,
      y: [-15 - (i % 5) * 8, 15 + (i % 7) * 6],
      x: [-12 - (i % 4) * 6, 12 + (i % 6) * 7],
      duration: 5 + (i % 6),
      delay: (i % 5) * 0.6,
    };
  });

  return (
    <div className="absolute inset-0">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          animate={{
            y: particle.y,
            x: particle.x,
            opacity: [0, 1, 0]
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            delay: particle.delay
          }}
          className="absolute w-2 h-2 bg-emerald-400/30 rounded-full"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`
          }}
        />
      ))}
    </div>
  );
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
          className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-emerald-200 from-opacity-30 to-teal-200 to-opacity-30 rounded-full blur-3xl"
        />
        <motion.div 
          animate={{ rotate: -360 }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
          className="absolute bottom-20 right-20 w-[500px] h-[500px] bg-gradient-to-tr from-blue-200 from-opacity-30 to-purple-200 to-opacity-30 rounded-full blur-3xl"
        />
        <motion.div 
          animate={{ y: [0, -30, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-amber-100 from-opacity-20 to-orange-100 to-opacity-20 rounded-full blur-3xl"
        />
      </div>

      {/* Floating Particles - Client Side Only */}
      <ClientOnlyParticles />

      <div className="max-w-7xl mx-auto relative z-10 px-6 lg:px-12 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-xs font-black uppercase tracking-widest mb-8 border border-emerald-200"
        >
          Exclusive Salon Growth Membership
        </motion.div>

        <motion.h1 
          className="text-5xl lg:text-8xl font-serif text-[#1A2520] mb-8 leading-[1.1]"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Elevate Your Salon <br />
          <span className="text-emerald-700 italic">Into a Digital Empire</span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 30 }} 
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-12"
        >
          Transform your salon with an intelligent virtual assistant that handles calls, 
          books appointments 24/7, and reduces no-shows by <span className="font-bold gradient-text">40%</span>
        </motion.p>

        {/* CTA Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }} 
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center gap-6 justify-center mb-16"
        >
          <motion.a 
            href="#demo" 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary group flex items-center gap-3 shadow-2xl"
          >
            <CalendarCheck className="w-5 h-5" />
            Try Live Demo
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </motion.a>
          
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link to="/login" className="inline-flex items-center gap-3 px-8 py-4 bg-white bg-opacity-80 backdrop-blur-md border-2 border-emerald-200 rounded-full font-semibold text-gray-800 hover:bg-emerald-50 transition-all duration-300 hover-lift">
              <Zap className="w-5 h-5 text-emerald-600" />
              Start Free Trial
            </Link>
          </motion.div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 50 }} 
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="bg-white bg-opacity-60 backdrop-blur-md rounded-3xl p-8 border border-emerald-100 hover-lift card-shadow"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <PhoneCall className="w-8 h-8 text-white" />
            </div>
            <div className="text-4xl font-bold gradient-text mb-2">24/7</div>
            <div className="text-gray-600 font-semibold">AI Call Handling</div>
          </motion.div>

          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="bg-white bg-opacity-60 backdrop-blur-md rounded-3xl p-8 border border-blue-100 hover-lift card-shadow"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <div className="text-4xl font-bold text-blue-600 mb-2">-40%</div>
            <div className="text-gray-600 font-semibold">No-Shows Reduced</div>
          </motion.div>

          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="bg-white bg-opacity-60 backdrop-blur-md rounded-3xl p-8 border border-amber-100 hover-lift card-shadow"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <div className="text-4xl font-bold text-amber-600 mb-2">3x</div>
            <div className="text-gray-600 font-semibold">Booking Efficiency</div>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div 
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-400"
      >
        <div className="w-6 h-10 border-2 border-gray-300 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-gray-400 rounded-full mt-2 animate-pulse"></div>
        </div>
      </motion.div>
    </section>
  );
}
