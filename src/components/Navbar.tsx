"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, ArrowRight, Sparkles, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <nav className={`fixed w-full z-50 transition-all duration-500 ${scrolled ? 'bg-white bg-opacity-90 backdrop-blur-md shadow-lg py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-12 flex justify-between items-center">
          
          {/* Logo */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <Link to="/" className="flex items-center gap-3 group">
              <motion.div
                whileHover={{ rotate: 180 }}
                transition={{ duration: 0.6 }}
                className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <Sparkles className="w-5 h-5 text-white" />
              </motion.div>
              <div className="flex flex-col">
                <span className="font-serif text-2xl font-bold text-gray-900 tracking-tight group-hover:text-emerald-600 transition-colors">
                  BookSmart
                </span>
                <span className="text-xs font-bold gradient-text">.ai</span>
              </div>
            </Link>
          </motion.div>
          
          {/* Desktop Navigation */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="hidden lg:flex items-center gap-10"
          >
            <div className="flex items-center gap-8 text-sm font-semibold text-gray-700">
              {['Solutions', 'Features', 'Pricing', 'Testimonials'].map((item, index) => (
                <motion.a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="relative group hover:text-emerald-600 transition-colors"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  {item}
                  <motion.div
                    className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 group-hover:w-full transition-all duration-300"
                  />
                </motion.a>
              ))}
            </div>
            
            <div className="flex items-center gap-4 pl-8 border-l border-gray-200">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link 
                  to="/staff" 
                  className="text-sm font-bold text-gray-700 hover:text-emerald-600 transition-colors flex items-center gap-2"
                >
                  <Phone className="w-4 h-4" />
                  Staff Management
                </Link>
              </motion.div>
              
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <a href="tel:+919513886363" className="flex items-center gap-2 px-6 py-3 bg-[#E9EFE6] text-[#2C3E35] rounded-full font-bold hover:bg-[#DCE6D9] transition shadow-sm group">
                  <Phone className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                  +91 95138 86363
                </a>
              </motion.div>
              
              <motion.a
                href="#demo"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-primary group flex items-center gap-2 shadow-lg"
              >
                Book Appointment
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </motion.a>
            </div>
          </motion.div>
          
          {/* Mobile Menu Toggle */}
          <motion.button 
            className="lg:hidden relative z-50"
            onClick={() => setMobileMenu(!mobileMenu)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <div className="w-10 h-10 bg-white bg-opacity-80 backdrop-blur-md rounded-xl flex items-center justify-center shadow-lg border border-gray-200">
              {mobileMenu ? <X className="w-5 h-5 text-gray-800" /> : <Menu className="w-5 h-5 text-gray-800" />}
            </div>
          </motion.button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenu && (
          <motion.div
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed inset-0 z-40 lg:hidden"
          >
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
              onClick={() => setMobileMenu(false)}
            />
            
            {/* Menu Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="absolute right-0 top-0 h-full w-80 bg-white bg-opacity-95 backdrop-blur-xl shadow-2xl border-l border-gray-200"
            >
              <div className="p-6 flex flex-col h-full">
                {/* Mobile Logo */}
                <div className="flex items-center justify-between mb-8">
                  <Link to="/" className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-serif text-xl font-bold text-gray-900">BookSmart.ai</span>
                  </Link>
                  <button
                    onClick={() => setMobileMenu(false)}
                    className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors"
                  >
                    <X className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
                
                {/* Navigation Links */}
                <nav className="flex-1">
                  <div className="space-y-2">
                    {['Solutions', 'Features', 'Pricing', 'Testimonials', 'Live Demo'].map((item, index) => (
                      <motion.a
                        key={item}
                        href={`#${item.toLowerCase().replace(' ', '-')}`}
                        onClick={() => setMobileMenu(false)}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="block px-4 py-3 text-lg font-semibold text-gray-700 hover:bg-emerald-50 hover:text-emerald-600 rounded-xl transition-all duration-200"
                      >
                        {item}
                      </motion.a>
                    ))}
                  </div>
                  
                  <div className="mt-8 pt-8 border-t border-gray-200 space-y-3">
                    <motion.a
                      href="/login"
                      onClick={() => setMobileMenu(false)}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 }}
                      className="block w-full px-6 py-3 bg-gray-100 text-gray-800 text-center rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                    >
                      Admin Login
                    </motion.a>
                    
                    <motion.a
                      href="#demo"
                      onClick={() => setMobileMenu(false)}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7 }}
                      className="block w-full btn-primary text-center shadow-lg"
                    >
                      Book Appointment
                    </motion.a>
                  </div>
                </nav>
                
                {/* Footer */}
                <div className="pt-8 border-t border-white/10 text-center text-xs font-bold text-gray-500 uppercase tracking-widest">
                  Direct Contact: +91 95138 86363 • 2026 BookSmart AI
                  <p className="mt-1">Elevating beauty businesses</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
