"use client";
import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { Check, X, Sparkles, Zap, ShieldCheck } from 'lucide-react';

export default function Pricing() {
  const [billingCycle, setBillingCycle] = useState('monthly');

  const plans = [
    {
      name: 'Starter Membership',
      description: 'Ideal for independent stylists and boutique studios.',
      price: billingCycle === 'monthly' ? 1999 : 1599,
      features: [
        'Digital AI Receptionist (24/7)',
        'Up to 100 Appointments/mo',
        'Basic SMS Reminders',
        'Single User Access',
        'Standard Business Dashboard',
        'Mobile Web Access',
        'Basic Analytics',
      ],
      notIncluded: [
        'Conversational Voice AI',
        'Multi-user Access',
        'Premium SEO Page',
        'Custom AI Training',
      ],
      icon: Zap,
      color: 'emerald',
      popular: false
    },
    {
      name: 'Professional Membership',
      description: 'Our most popular choice for busy teams and scaling salons.',
      price: billingCycle === 'monthly' ? 4999 : 3999,
      features: [
        'Everything in Starter',
        'Unlimited Appointments',
        'Conversational Voice AI (Exotel)',
        'Advanced Staff Analytics',
        'Multi-user Access Control',
        'Premium SEO Growth Page',
        'Priority Email Support',
        'Automated Review Manager',
      ],
      notIncluded: [
        'Multi-location Sync',
        'Custom AI Training',
        'Dedicated Account Manager',
      ],
      icon: Sparkles,
      color: 'teal',
      popular: true
    },
    {
      name: 'Enterprise Membership',
      description: 'The ultimate solution for salon chains and industry leaders.',
      price: billingCycle === 'monthly' ? 9999 : 7999,
      features: [
        'Everything in Professional',
        'Multi-location Sync & Mgmt',
        'Custom Model AI Training',
        'Dedicated Account Manager',
        'Priority Phone Support',
        'Custom API & Integrations',
        'White Label Branding',
        'On-site Training & Setup',
      ],
      notIncluded: [],
      icon: ShieldCheck,
      color: 'blue',
      popular: false
    }
  ];

  return (
    <main className="min-h-screen bg-[#FAF9F6]">
      <Navbar />
      
      {/* Hero Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-emerald-50 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2 opacity-50" />
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-black uppercase tracking-widest mb-8 border border-emerald-200"
          >
            Membership Strategy
          </motion.div>
          <h1 className="text-5xl lg:text-7xl font-serif text-[#1A2520] mb-8 leading-tight">
            Invest in Your <span className="text-emerald-700">Growth</span>
          </h1>
          <p className="text-xl text-[#2C3E35]/70 max-w-3xl mx-auto mb-12 font-medium">
            Choose the membership that aligns with your salon's production scale. 
            All memberships include our core digital receptionist engine.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-6 mb-16">
            <span className={`text-lg transition-all ${billingCycle === 'monthly' ? 'text-[#1A2520] font-bold' : 'text-gray-400'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-10 w-20 items-center rounded-full bg-[#1A2520] p-1 transition-colors"
            >
              <div
                className={`flex h-8 w-8 transform items-center justify-center rounded-full bg-emerald-500 transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-10' : 'translate-x-0'
                }`}
              >
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
              </div>
            </button>
            <span className={`text-lg transition-all ${billingCycle === 'yearly' ? 'text-[#1A2520] font-bold' : 'text-gray-400'}`}>
              Yearly
              <span className="ml-3 inline-block px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-black rounded-full">Save 20%</span>
            </span>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20 px-6 bg-white border-t border-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {plans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`relative rounded-[3rem] p-10 flex flex-col transition-all duration-500
                  ${plan.popular 
                    ? 'bg-[#1A2520] text-emerald-50 shadow-2xl scale-105 z-20 border-0' 
                    : 'bg-[#FAF9F6] border border-gray-100 shadow-xl'}`}
              >
                {plan.popular && (
                  <div className="absolute -top-5 left-1/2 transform -translate-x-1/2">
                    <span className="bg-emerald-500 text-white px-6 py-2 rounded-full text-xs font-black uppercase tracking-widest shadow-lg">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="mb-10">
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 
                      ${plan.popular ? 'bg-white/10 text-emerald-400' : 'bg-emerald-100 text-emerald-700'}`}>
                    <plan.icon className="w-7 h-7" />
                  </div>
                  <h3 className="text-2xl font-serif font-bold mb-3">{plan.name}</h3>
                  <p className={`text-sm font-medium leading-relaxed ${plan.popular ? 'text-emerald-100/60' : 'text-gray-500'}`}>
                    {plan.description}
                  </p>
                </div>

                <div className="mb-12 flex items-baseline gap-2">
                  <span className="text-5xl font-black">₹{plan.price.toLocaleString('en-IN')}</span>
                  <span className={`text-sm font-bold uppercase tracking-wider ${plan.popular ? 'text-emerald-100/40' : 'text-gray-400'}`}>
                    / mo
                  </span>
                </div>

                <div className="space-y-4 mb-12 flex-1">
                  {plan.features.map((feature, fIndex) => (
                    <div key={fIndex} className="flex items-start gap-3">
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5
                          ${plan.popular ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'}`}>
                        <Check className="w-3 h-3" />
                      </div>
                      <span className={`text-sm font-medium ${plan.popular ? 'text-emerald-50/80' : 'text-[#2C3E35]'}`}>
                        {feature}
                      </span>
                    </div>
                  ))}
                  {plan.notIncluded.map((feature, fIndex) => (
                    <div key={fIndex} className="flex items-start gap-3 opacity-30">
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5
                          ${plan.popular ? 'bg-white/10' : 'bg-gray-200'}`}>
                        <X className="w-3 h-3" />
                      </div>
                      <span className="text-sm font-medium">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  className={`w-full py-5 rounded-[2rem] font-black uppercase tracking-widest text-xs transition-all duration-300
                    ${plan.popular
                      ? 'bg-emerald-500 text-white hover:bg-emerald-400 shadow-xl shadow-emerald-500/20'
                      : 'bg-[#1A2520] text-white hover:bg-[#2C3E35] shadow-lg'}`}
                >
                  Join Membership
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 px-6 bg-[#FAF9F6]">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-serif font-bold text-[#1A2520] mb-4">Membership FAQ</h2>
            <p className="text-[#2C3E35]/60 font-medium italic">Everything you need to know about scaling your salon</p>
          </div>
          <div className="space-y-6">
            {[
              { q: "Can I upgrade my growth membership?", a: "Absolutely. Most salons start with our Professional membership and scale to Enterprise as they add locations." },
              { q: "Is the Voice AI included in all plans?", a: "Conversational Voice AI is available from our Professional Membership tier upwards to ensure high-end support for busy teams." },
              { q: "How does the savings logic work?", a: "Our annual strategy members save 20% compared to monthly memberships, allowing you to reinvest more into your business." },
              { q: "Can I cancel my membership?", a: "Yes. Our membership is month-to-month with no long-term lock-ins. We grow only when you grow." }
            ].map((faq, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100 hover:shadow-md transition"
              >
                <h3 className="text-lg font-bold text-[#1A2520] mb-3">{faq.q}</h3>
                <p className="text-sm text-[#2C3E35]/70 font-medium leading-relaxed">{faq.a}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[#1A2520]" />
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_30%_20%,rgba(16,185,129,0.1),transparent)]" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-4xl lg:text-5xl font-serif font-bold text-white mb-8">
            Ready to Begin Your Growth Journey?
          </h2>
          <p className="text-xl text-emerald-100/70 mb-12 font-medium">
            Join the collective of 500+ premium salons that have already digitalized their front desk.
          </p>
          <button className="bg-emerald-500 text-white px-12 py-5 rounded-full font-black uppercase tracking-widest text-xs hover:bg-emerald-400 transition shadow-2xl shadow-emerald-500/20">
            Start Strategy Session
          </button>
        </div>
      </section>

      <Footer />
    </main>
  );
}
