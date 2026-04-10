"use client";
import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { Quote, Star, Users, TrendingUp, ShieldCheck, Heart } from 'lucide-react';

export default function Testimonials() {
  const [activeFilter, setActiveFilter] = useState('all');

  const testimonials = [
    {
      id: 1,
      name: 'Sarah Johnson',
      role: 'Founding Member',
      business: 'Bella Beauty Premier',
      location: 'Mumbai, India',
      image: 'https://images.unsplash.com/photo-1494790108755-2616b332c1cd?w=100&h=100&fit=crop&crop=face',
      rating: 5,
      content: 'The growth membership is a game changer. We don\'t just get a software; we get a digital partner that handles 90% of our front-desk logic. Our monthly revenue grew by 60% in the first quarter.',
      category: 'salon',
      results: ['60% Revenue Growth', '90% Reception Automation', 'Seamless AI Call Scaling']
    },
    {
      id: 2,
      name: 'Michael Chen',
      role: 'Professional Member',
      business: 'Style Studio Elite',
      location: 'Bangalore, India',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
      rating: 5,
      content: 'The Voice AI integration is why we joined. Our clients calling the Exotel line are wowed by the natural responses. It\'s like having a senior receptionist available 24/7.',
      category: 'spa',
      results: ['No-show rate dropped to 2%', '24/7 Voice Coverage', 'Professional Brand Image']
    },
    {
      id: 3,
      name: 'Priya Sharma',
      role: 'Enterprise Partner',
      business: 'Glow Wellness Chain',
      location: 'Delhi, India',
      image: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop&crop=face',
      rating: 5,
      content: 'With 15 locations, we needed a membership that could scale with us. The multi-location sync and dedicated account manager make management effortless.',
      category: 'wellness',
      results: ['15 Locations Synced', 'Enterprise-grade Security', 'Custom AI Training']
    }
  ];

  return (
    <main className="min-h-screen bg-[#FAF9F6]">
      <Navbar />
      
      {/* Hero Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-emerald-50 blur-[120px] rounded-full opacity-50" />
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-xs font-black uppercase tracking-widest mb-8"
          >
            Member Success Stories
          </motion.div>
          <h1 className="text-5xl lg:text-7xl font-serif text-[#1A2520] mb-8 leading-tight">
            Voices of Our <br />
            <span className="text-emerald-700 italic">Strategic Partners</span>
          </h1>
          <p className="text-xl text-[#2C3E35]/70 max-w-3xl mx-auto mb-16 font-medium">
            Hear from the salon owners who have transitioned to a digital-first 
            membership model and achieved unprecedented growth.
          </p>
          
          {/* Stats Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12 max-w-5xl mx-auto">
            {[
              { label: 'Strategic Members', val: '500+', icon: Users },
              { label: 'Average Growth', val: '65%', icon: TrendingUp },
              { label: 'Uptime Reliability', val: '99.9%', icon: ShieldCheck },
              { label: 'Member Love', val: '4.9/5', icon: Heart }
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100"
              >
                <stat.icon className="w-6 h-6 text-emerald-600 mx-auto mb-4" />
                <div className="text-3xl font-black text-[#1A2520] mb-1">{stat.val}</div>
                <div className="text-[10px] font-black uppercase tracking-widest text-[#2C3E35]/40">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Grid */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {testimonials.map((t, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="relative bg-[#FAF9F6] rounded-[3rem] p-10 border border-gray-100 flex flex-col"
              >
                <Quote className="absolute top-8 right-8 w-12 h-12 text-emerald-700/5 rotate-180" />
                
                <div className="flex items-center gap-4 mb-8">
                  <img src={t.image} alt={t.name} className="w-14 h-14 rounded-2xl object-cover shadow-md" />
                  <div>
                    <h3 className="text-lg font-bold text-[#1A2520]">{t.name}</h3>
                    <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider">{t.role}</p>
                    <p className="text-[10px] text-gray-400 font-medium">{t.business} • {t.location}</p>
                  </div>
                </div>

                <div className="flex gap-1 mb-6">
                  {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 fill-emerald-500 text-emerald-500" />)}
                </div>

                <p className="text-[#2C3E35]/70 font-medium leading-relaxed mb-8 flex-1 italic">
                  "{t.content}"
                </p>

                <div className="pt-8 border-t border-gray-200">
                  <div className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Strategic Impact</div>
                  <div className="space-y-3">
                    {t.results.map((res, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className="w-5 h-5 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center">
                          <TrendingUp className="w-3 h-3" />
                        </div>
                        <span className="text-xs font-bold text-[#1A2520]">{res}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[#1A2520]" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-4xl lg:text-5xl font-serif font-bold text-white mb-8">
            Become a Success Story
          </h2>
          <p className="text-xl text-emerald-100/70 mb-12 font-medium">
            Join the strategic collective of salon owners digitizing the future.
          </p>
          <button className="bg-emerald-500 text-white px-12 py-5 rounded-full font-black uppercase tracking-widest text-xs hover:bg-emerald-400 transition shadow-2xl">
            Join Membership Now
          </button>
        </div>
      </section>

      <Footer />
    </main>
  );
}
