"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Phone, CalendarCheck, BarChart3, MessageSquare, Zap, Clock, Star } from 'lucide-react';

export default function Features() {
  const features = [
    {
      title: '24/7 Digital Employee',
      description: 'Your salon is always open. Your digital receptionist handles incoming calls and web queries, booking slots directly into your calendar without a human needed.',
      icon: Phone,
      gradient: 'from-emerald-400 to-teal-500',
      stats: '24/7',
    },
    {
      title: 'Automated Growth Engine',
      description: 'Maximize your retention. The platform automatically dispatches customized SMS and email reminders to ensure your seats stay full and no-shows vanish.',
      icon: CalendarCheck,
      gradient: 'from-blue-400 to-indigo-500',
      stats: 'Auto',
    },
    {
      title: 'Real-Time Intelligence Hub',
      description: 'Monitor your scale with ease. Get crystal clear visibility into your revenue, staff efficiency, and service performance from your private membership portal.',
      icon: BarChart3,
      gradient: 'from-amber-400 to-orange-500',
      stats: 'Live',
    },
    {
      title: 'Growth-Specific AI Brain',
      description: 'Your partner is trained on high-end salon terminology and pricing psychology. It understands your business context exactly as you do.',
      icon: MessageSquare,
      gradient: 'from-purple-400 to-pink-500',
      stats: '100%',
    },
  ];

  return (
    <section id="features" className="relative py-32 bg-gradient-to-br from-gray-50 via-white to-emerald-50 overflow-hidden">
      
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="absolute top-10 right-10 w-[400px] h-[400px] bg-gradient-to-br from-emerald-100/20 to-teal-100/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
          className="absolute bottom-10 left-10 w-[300px] h-[300px] bg-gradient-to-tr from-blue-100/20 to-purple-100/20 rounded-full blur-3xl"
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12">
        
        {/* Section Header */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto mb-20"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white bg-opacity-10 backdrop-blur-md border border-emerald-200 border-opacity-50 mb-8"
          >
            <Zap className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-semibold text-emerald-700">Powerful Features</span>
          </motion.div>
          
          <h2 className="text-5xl md:text-6xl font-serif font-bold text-gray-900 mb-6 leading-tight">
            Grow your business while we<br />
            <span className="gradient-text">handle the front desk</span>
          </h2>
          
          <p className="text-xl text-gray-600 font-medium max-w-3xl mx-auto leading-relaxed">
            Our AI serves as your reliable receptionist, going beyond basic booking to actively 
            manage your schedule and engage your clients.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-20">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: idx * 0.2 }}
              whileHover={{ scale: 1.02 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              
              <div className="relative bg-white bg-opacity-80 backdrop-blur-sm rounded-3xl p-10 border border-gray-100 hover:border-emerald-200 transition-all duration-300 hover-lift card-shadow">
                
                {/* Icon and Stats */}
                <div className="flex items-start gap-6 mb-6">
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className={`w-20 h-20 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
                  >
                    <feature.icon className="w-10 h-10 text-white" />
                  </motion.div>
                  
                  <div className="flex-1">
                    <div className={`inline-block px-3 py-1 bg-gradient-to-r ${feature.gradient} text-white text-sm font-bold rounded-full mb-3`}>
                      {feature.stats} Success Rate
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                    <p className="text-gray-600 font-medium leading-relaxed">{feature.description}</p>
                  </div>
                </div>

                {/* Hover Effect Line */}
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: "100%" }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: idx * 0.2 + 0.3 }}
                  className={`h-1 bg-gradient-to-r ${feature.gradient} rounded-full mt-6`}
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-3xl p-12 text-white relative overflow-hidden">
            <div className="absolute inset-0 bg-black bg-opacity-10" />
            <div className="relative z-10">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-md rounded-2xl flex items-center justify-center mx-auto mb-6"
              >
                <Star className="w-8 h-8 text-white" />
              </motion.div>
              
              <h3 className="text-3xl md:text-4xl font-serif font-bold mb-4">
                Ready to transform your salon?
              </h3>
              <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                Join hundreds of salons that have already increased their booking efficiency by 300%
              </p>
              
              <motion.a
                href="#demo"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-flex items-center gap-3 px-8 py-4 bg-white text-emerald-600 rounded-full font-bold hover:bg-gray-100 transition-all duration-300 shadow-xl"
              >
                <Clock className="w-5 h-5" />
                Start Your Free Trial
              </motion.a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
