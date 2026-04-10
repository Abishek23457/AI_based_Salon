"use client";
import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { 
  Zap, Phone, CalendarCheck, BarChart3, MessageSquare, 
  ShieldCheck, Share2, Star, Clock, Globe
} from 'lucide-react';

export default function Features() {
  const coreBenefits = [
    {
      title: 'Digital AI Employee',
      description: 'A 24/7 intelligent partner that handles your front desk, answers client queries, and books appointments while you focus on styling.',
      icon: Phone,
      color: 'emerald'
    },
    {
      title: 'Smart Growth Scheduling',
      description: 'Intelligent booking logic that eliminates conflicts and optimizes your staff chairs for maximum revenue per hour.',
      icon: CalendarCheck,
      color: 'blue'
    },
    {
      title: 'Digital Management Panel',
      description: 'Full visibility into your salon membership performance. Manage staff, services, and locations from one premium dashboard.',
      icon: ShieldCheck,
      color: 'purple'
    }
  ];

  const membershipPerks = [
    {
      title: 'Growth Reminders',
      description: 'Automated SMS & Email reminders that reduce no-shows by 90% and keep your seats full.',
      icon: Clock
    },
    {
      title: 'Intelligence Hub',
      description: 'Real-time analytics on revenue, staff efficiency, and customer satisfaction metrics.',
      icon: BarChart3
    },
    {
      title: 'Conversational Voice',
      description: 'Professional telephony integration (Exotel) with Speech-to-Speech logic for natural phone bookings.',
      icon: Share2
    },
    {
      title: 'SEO Member Page',
      description: 'A premium, SEO-optimized landing page for your salon to drive more independent traffic.',
      icon: Globe
    }
  ];

  return (
    <main className="min-h-screen bg-[#FAF9F6]">
      <Navbar />
      
      {/* Hero Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1/3 h-1/3 bg-emerald-50 blur-[100px] rounded-full opacity-50" />
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-xs font-black uppercase tracking-widest mb-8"
          >
            Membership Benefits
          </motion.div>
          <h1 className="text-5xl lg:text-7xl font-serif text-[#1A2520] mb-8 leading-tight">
            The Digital Frontier of <br />
            <span className="text-emerald-700 italic">Salon Management</span>
          </h1>
          <p className="text-xl text-[#2C3E35]/70 max-w-3xl mx-auto mb-12 font-medium">
            Your BookSmart membership unlocks a professional digital workforce and 
            automation infrastructure designed to scale your business.
          </p>
        </div>
      </section>
 
      {/* Core Benefits */}
      <section className="py-20 px-6 bg-white border-y border-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {coreBenefits.map((benefit, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="text-center group"
              >
                <div className={`w-20 h-20 rounded-3xl mx-auto mb-8 flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 shadow-lg
                  ${benefit.color === 'emerald' ? 'bg-emerald-100 text-emerald-700' : 
                    benefit.color === 'blue' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'}`}>
                  <benefit.icon className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-serif font-bold text-[#1A2520] mb-4">{benefit.title}</h3>
                <p className="text-[#2C3E35]/60 font-medium leading-relaxed">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Membership Perks Grid */}
      <section className="py-24 px-6 bg-[#FAF9F6]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-serif font-bold text-[#1A2520] mb-4">Membership Essentials</h2>
            <p className="text-[#2C3E35]/60 font-medium italic">Standard in every professional and enterprise tier</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {membershipPerks.map((perk, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-sm hover:shadow-xl transition-all duration-300"
              >
                <div className="w-12 h-12 bg-[#FAF9F6] text-emerald-600 rounded-xl flex items-center justify-center mb-6">
                  <perk.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-[#1A2520] mb-3">{perk.title}</h3>
                <p className="text-sm text-[#2C3E35]/70 font-medium leading-relaxed">{perk.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[#1A2520]" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center mx-auto mb-8"
          >
            <Star className="w-8 h-8 text-emerald-400" />
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-serif font-bold text-white mb-8">
            Elevate Your Salon Standard
          </h2>
          <p className="text-xl text-emerald-100/70 mb-12 font-medium">
            Join the membership that understands the art and science of salon growth.
          </p>
          <button className="bg-emerald-500 text-white px-12 py-5 rounded-full font-black uppercase tracking-widest text-xs hover:bg-emerald-400 transition shadow-2xl shadow-emerald-500/20">
            Join the Membership
          </button>
        </div>
      </section>

      <Footer />
    </main>
  );
}
