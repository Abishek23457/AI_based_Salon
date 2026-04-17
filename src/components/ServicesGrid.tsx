"use client";
import React, { useEffect, useState } from 'react';
import { API_URL } from '../api';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

interface Service {
  id: number;
  name: string;
  duration_minutes: number;
  price: number;
  description: string;
}

export default function ServicesGrid() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/services/`)
      .then(res => res.json())
      .then(data => {
        setServices(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Could not fetch services:", err);
        setLoading(false);
      });
  }, []);

  return (
    <section id="services" className="py-24 bg-white px-6 lg:px-12 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-serif text-[#1A2520] mb-4">Our Curated Offerings</h2>
          <p className="text-[#2C3E35]/60 font-medium">Experience premium care with transparent pricing.</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20 text-[#4A6B53] font-medium animate-pulse">Loading Services Catalog...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, idx) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="bg-[#FAF9F6] p-8 rounded-[2rem] hover:shadow-xl transition-all border border-gray-100 group cursor-pointer hover:-translate-y-1"
              >
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mb-6 shadow-sm text-[#4A6B53] group-hover:scale-110 transition">
                  <Clock className="w-5 h-5" />
                </div>
                <h3 className="text-2xl font-serif font-bold text-[#1A2520] mb-2">{service.name}</h3>
                <p className="text-gray-500 text-sm mb-6 line-clamp-2 leading-relaxed">{service.description}</p>
                <div className="flex justify-between items-end border-t border-gray-200/50 pt-4">
                  <span className="text-sm font-medium text-gray-400">{service.duration_minutes} Mins</span>
                  <span className="text-xl font-bold text-[#2C3E35]">₹{service.price}</span>
                </div>
              </motion.div>
            ))}
            
            {services.length === 0 && (
                <div className="col-span-full text-center text-gray-500 p-10 bg-[#FAF9F6] border border-dashed border-gray-300 rounded-3xl">
                  No services found in the database. Please add them via the API or initialization payload.
                </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
