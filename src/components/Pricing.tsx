"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, ShieldCheck } from 'lucide-react';

const plans = [
  {
    name: 'Starter Membership',
    price: '₹1,999',
    period: '/mo',
    description: 'Perfect for independent stylists and boutique studios starting their digital journey.',
    features: [
      'Digital AI Receptionist (24/7)',
      'Up to 100 Appointments/mo',
      'Basic SMS Reminders',
      'Single User Access',
      'Standard Business Dashboard',
    ],
    icon: Zap,
    color: 'emerald',
    popular: false,
  },
  {
    name: 'Professional Membership',
    price: '₹4,999',
    period: '/mo',
    description: 'Our most popular choice for busy teams and growing salon businesses.',
    features: [
      'Everything in Starter',
      'Unlimited Appointments',
      'Conversational Voice AI (Exotel)',
      'Advanced Staff Analytics',
      'Multi-user Access Control',
      'Premium SEO Growth Page',
    ],
    icon: Sparkles,
    color: 'teal',
    popular: true,
  },
  {
    name: 'Enterprise Membership',
    price: '₹9,999',
    period: '/mo',
    description: 'The ultimate solution for salon chains and high-volume luxury studios.',
    features: [
      'Everything in Professional',
      'Multi-location Sync & Mgmt',
      'Custom Model AI Training',
      'Dedicated Account Manager',
      'Priority Support Line',
      'Custom API & Integrations',
    ],
    icon: ShieldCheck,
    color: 'blue',
    popular: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-[#E9EFE6] px-6 lg:px-12 relative overflow-hidden">
      {/* Background Ornaments */}
      <div className="absolute top-0 right-0 w-1/3 h-1/3 bg-emerald-100/50 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-1/4 h-1/4 bg-teal-100/50 blur-[120px] rounded-full translate-y-1/2 -translate-x-1/2" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-black uppercase tracking-widest mb-6"
          >
            Membership Plans
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-serif text-[#1A2520] mb-6">Invest in Your Growth</h2>
          <p className="max-w-2xl mx-auto text-[#2C3E35]/60 font-medium text-lg leading-relaxed">
            Choose the membership that fits your salon's scale. All plans include our core AI scheduling engine and digital partner support.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className={`relative bg-white p-10 rounded-[2.5rem] border ${plan.popular ? 'border-[#4A6B53] shadow-2xl scale-105 z-20' : 'border-gray-100 shadow-xl'} flex flex-col`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 px-6 py-2 bg-[#2C3E35] text-white text-xs font-black uppercase tracking-widest rounded-full shadow-lg">
                  Most Popular
                </div>
              )}

              <div className="mb-8">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 
                    ${plan.color === 'emerald' ? 'bg-emerald-50 text-emerald-600' : 
                      plan.color === 'teal' ? 'bg-teal-50 text-teal-600' : 'bg-blue-50 text-blue-600'}`}>
                  <plan.icon className="w-7 h-7" />
                </div>
                <h3 className="text-2xl font-serif font-bold text-[#1A2520] mb-2">{plan.name}</h3>
                <p className="text-gray-500 text-sm font-medium leading-relaxed">{plan.description}</p>
              </div>

              <div className="mb-10 flex items-end gap-1">
                <span className="text-4xl font-bold text-[#1A2520]">{plan.price}</span>
                <span className="text-gray-400 font-semibold mb-1">{plan.period}</span>
              </div>

              <div className="space-y-4 mb-10 flex-1">
                {plan.features.map(feature => (
                  <div key={feature} className="flex items-start gap-3">
                    <div className="w-5 h-5 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-3 h-3" />
                    </div>
                    <span className="text-[#2C3E35] text-sm font-medium">{feature}</span>
                  </div>
                ))}
              </div>

              <button className={`w-full py-4 rounded-2xl font-bold transition-all duration-300
                  ${plan.popular ? 'bg-[#2C3E35] text-white hover:bg-[#1A2520] shadow-lg shadow-emerald-900/10' : 'bg-gray-50 text-[#2C3E35] hover:bg-gray-100'}`}>
                Join Membership
              </button>
            </motion.div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-500 font-medium">
            Not sure which membership is right for you? <a href="#demo" className="text-emerald-600 underline font-bold">Book a free strategy session</a> or contact our growth team.
          </p>
        </div>
      </div>
    </section>
  );
}
