"use client";
import React from 'react';
import { motion } from 'framer-motion';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Features from '../components/Features';
import BookingForm from '../components/BookingForm';
import ChatWidget from '../components/ChatWidget';
import ClientOnly from '../components/ClientOnly';

import Pricing from '../components/Pricing';
import Testimonials from '../components/Testimonials';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <Hero />
      <Features />
      
      <Testimonials />
      <Pricing />
      
      {/* Demo Section */}
      <section id="demo" className="py-24 bg-[#1A2520] text-white">
        <div className="max-w-7xl mx-auto px-6 text-center mb-16">
          <div className="inline-block px-4 py-1.5 bg-white/10 text-emerald-300 rounded-full text-xs font-black uppercase tracking-widest mb-6 border border-white/10 backdrop-blur-sm">
            Live Demo
          </div>
          <h2 className="text-4xl lg:text-5xl font-serif mb-6">Experience the Growth Engine</h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto font-medium">
            Test the professional digital infrastructure included in every membership. Automate the details and scale your salon empire.
          </p>
        </div>
        <div className="max-w-4xl mx-auto px-6">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white rounded-[2.5rem] p-1 shadow-2xl overflow-hidden"
          >
            <div className="bg-[#FAF9F6] rounded-[2.2rem] p-10">
              <ClientOnly>
                <BookingForm />
              </ClientOnly>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
      
      <ClientOnly>
        <ChatWidget />
      </ClientOnly>
    </main>
  );
}
