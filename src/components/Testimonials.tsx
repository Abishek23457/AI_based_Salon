"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Star, Quote, ChevronLeft, ChevronRight } from 'lucide-react';

const testimonials = [
  {
    name: "Priya Sharma",
    role: "Owner, Bloom Bloom Salon",
    content: "BookSmart AI has completely transformed our booking process. Our AI receptionist handles 70% of calls now, giving us more time to focus on our clients. The recovery of missed appointments alone paid for the subscription!",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150&h=150",
  },
  {
    name: "Rohan Mehra",
    role: "Director, Urban Scissors",
    content: "The analytics dashboard is a game-changer. I can finally see which services are truly profitable and manage my staff's schedule across three locations from my phone. Absolutely 'Production Ready' software.",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150&h=150",
  },
  {
    name: "Anjali Gupta",
    role: "Lead Stylist, Aura Luxury Spa",
    content: "The automated SMS reminders have reduced our no-shows by nearly 90%. My clients love the professional experience and I love not having to manually text every appointment myself.",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=150&h=150",
  },
];

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-24 bg-white px-6 lg:px-12 relative overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-block px-4 py-1.5 bg-[#E9EFE6] text-[#4A6B53] rounded-full text-xs font-black uppercase tracking-widest mb-6">
              Success Stories
            </div>
            <h2 className="text-4xl lg:text-5xl font-serif text-[#1A2520] mb-8 leading-tight">
              Trusted by 500+ <br/>
              <span className="text-emerald-700">Premium Salons</span> Worldwide
            </h2>
            <p className="text-gray-600 font-medium text-lg leading-relaxed mb-10 max-w-md">
              Hear from business owners who have optimized their operations and recovered thousands in revenue using our AI-driven system.
            </p>
            
            <div className="flex items-center gap-6">
              <div className="flex -space-x-4">
                {[1,2,3,4].map(i => (
                  <div key={i} className="w-12 h-12 rounded-full border-4 border-white overflow-hidden shadow-md">
                    <img src={`https://i.pravatar.cc/150?u=${i + 10}`} alt="User" />
                  </div>
                ))}
              </div>
              <div>
                <div className="flex text-amber-500 mb-1">
                  {[1,2,3,4,5].map(i => <Star key={i} className="w-4 h-4 fill-current" />)}
                </div>
                <p className="text-sm font-bold text-[#1A2520]">4.9/5 Rating by 2k+ Admins</p>
              </div>
            </div>
          </motion.div>

          <div className="relative">
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-emerald-50 rounded-full blur-[80px]" />
            <div className="space-y-6">
              {testimonials.map((t, idx) => (
                <motion.div
                  key={t.name}
                  initial={{ opacity: 0, x: 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: idx * 0.2 }}
                  className="bg-[#FAF9F6] p-8 rounded-[2rem] border border-gray-100 shadow-sm relative group hover:shadow-lg transition-all"
                >
                  <div className="absolute top-8 right-8 text-[#4A6B53]/10 group-hover:text-[#4A6B53]/20 transition-colors">
                    <Quote className="w-12 h-12 fill-current" />
                  </div>
                  
                  <div className="flex items-center gap-4 mb-6">
                    <img src={t.avatar} alt={t.name} className="w-14 h-14 rounded-2xl object-cover shadow-md" />
                    <div>
                      <h4 className="font-bold text-[#1A2520]">{t.name}</h4>
                      <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">{t.role}</p>
                    </div>
                  </div>
                  
                  <p className="text-[#2C3E35] font-medium leading-relaxed italic">
                    &quot;{t.content}&quot;
                  </p>
                </motion.div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
