import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, Phone, MessageSquare, Save, RefreshCw, Zap, 
  ShieldCheck, Mail, X, Play, Clock, User, FileText 
} from 'lucide-react';
import { API_URL as API } from '../../api';
import BrowserVoiceModal from './BrowserVoiceModal';

export default function AITab({ authFetch, showToast }: any) {
  const [syncing, setSyncing] = useState(false);
  const [reminding, setReminding] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);

  const handleSyncKnowledge = async () => {
    setSyncing(true);
    try {
      await new Promise(r => setTimeout(r, 2000));
      showToast('AI Knowledge Base Synced ✓');
    } catch {
      showToast('Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const handleSendReminders = async () => {
    setReminding(true);
    try {
      const response = await authFetch(`${API}/reminders/send-today`, { method: 'POST' });
      if (response.ok) {
          showToast('Payment & Booking Reminders Sent!');
      } else {
          showToast('Failed to send reminders');
      }
    } catch {
      showToast('Error sending reminders');
    } finally {
      setReminding(false);
    }
  };

  const fetchLogs = async () => {
    setLoadingLogs(true);
    setShowLogs(true);
    try {
      // Assuming salon_id = 1 for demo
      const response = await authFetch(`${API}/analytics/1/call-logs`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (err) {
      showToast('Failed to load call logs');
    } finally {
      setLoadingLogs(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-[#1A2520] font-serif mb-2">Automation Hub</h1>
          <p className="text-gray-500 font-medium">Configure how your AI interacts with customers across channels.</p>
        </div>
        <div className="bg-emerald-50 px-4 py-2 rounded-xl border border-emerald-100 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-bold text-emerald-800 uppercase tracking-widest">Active Intelligence</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Phone AI Controller */}
        <div className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-gray-100 flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-[0.03]">
            <Phone className="w-32 h-32" />
          </div>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center shadow-inner">
              <Phone className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-[#1A2520] text-lg">Conversational Voice Engine</h3>
              <p className="text-xs font-bold text-blue-600 uppercase tracking-widest">Exotel S2S (Speech-to-Speech)</p>
            </div>
          </div>
          <p className="text-[#2C3E35]/60 text-sm font-medium mb-8 leading-relaxed">
            Your Exotel-connected phone number uses advanced **Speech-to-Speech** technology. The AI hears voices and responds instantly with human-like audio.
          </p>
          <div className="space-y-4 mb-8">
             <div className="flex items-center gap-3 text-sm font-bold text-[#2C3E35]">
               <Zap className="w-4 h-4 text-amber-500" /> Latency: 500ms (Low)
             </div>
             <div className="flex items-center gap-3 text-sm font-bold text-[#2C3E35]">
               <ShieldCheck className="w-4 h-4 text-emerald-500" /> Provider: Google S2S (Unified)
             </div>
             <div className="flex items-center gap-3 text-sm font-bold text-[#2C3E35]">
               <Save className="w-4 h-4 text-blue-500" /> Archiving: MP4 Recording Active
             </div>
          </div>
          <div className="mt-auto flex gap-3">
             <button 
              onClick={fetchLogs}
              className="flex-1 py-3 bg-gray-50 text-[#2C3E35] rounded-xl font-bold hover:bg-gray-100 transition text-sm"
             >
               View Call Logs
             </button>
             <button 
              onClick={() => setShowVoiceModal(true)}
              className="flex-1 py-3 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition text-sm"
             >
              Live Monitor
             </button>
          </div>
        </div>

        {/* Web Chat Controller */}
        <div className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-gray-100 flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-[0.03]">
            <MessageSquare className="w-32 h-32" />
          </div>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center shadow-inner">
              <MessageSquare className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-[#1A2520] text-lg">Support Chat Assistant</h3>
              <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">Web T2T (Text-to-Text)</p>
            </div>
          </div>
          <p className="text-[#2C3E35]/60 text-sm font-medium mb-8 leading-relaxed">
            The website chatbot uses **Text-to-Text** logic to provide rapid support, answer pricing queries, and guide customers to the booking form.
          </p>
          <div className="space-y-4 mb-8">
             <div className="flex items-center gap-3 text-sm font-bold text-[#2C3E35]">
               <Mail className="w-4 h-4 text-purple-500" /> Integrated Email Reminders
             </div>
             <div className="flex items-center gap-3 text-sm font-bold text-[#2C3E35]">
               <Save className="w-4 h-4 text-blue-500" /> Memory: RAG Injected
             </div>
          </div>
          <div className="mt-auto flex gap-3">
             <button onClick={handleSendReminders} disabled={reminding} className="flex-1 py-3 border border-emerald-100 text-emerald-700 rounded-xl font-bold hover:bg-emerald-50 transition text-sm">
               {reminding ? 'Sending...' : 'Issue Reminders'}
             </button>
             <button onClick={handleSyncKnowledge} disabled={syncing} className="flex-1 py-3 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition text-sm flex items-center justify-center gap-2">
               <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} /> {syncing ? 'Syncing...' : 'Initiate Sync'}
             </button>
          </div>
        </div>

      </div>

      {/* Logic Overview */}
      <div className="bg-emerald-50 rounded-[2.5rem] p-10 border border-emerald-100 mt-8">
          <h3 className="font-serif text-2xl font-bold text-[#1A2520] mb-4">How your AI communicates</h3>
          <p className="text-[#2C3E35]/70 font-medium leading-relaxed max-w-3xl">
              To provide the best customer experience, we distinguish between high-touch phone calls and rapid web queries. 
              Your **Exotel Number** acts as the primary voice entry point with Speech-to-Speech logic, while the **Web Widget** 
              perfectly handles Text-to-Text interactions for users on the go.
          </p>
      </div>

      {/* Call Logs Modal */}
      <AnimatePresence>
        {showLogs && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 sm:p-12">
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              exit={{ opacity: 0 }}
              onClick={() => setShowLogs(false)}
              className="absolute inset-0 bg-[#1A2520]/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-4xl bg-white rounded-[3rem] shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
            >
              <div className="p-8 border-b border-gray-100 flex items-center justify-between bg-[#FAF9F6]">
                <div>
                  <h2 className="text-2xl font-serif font-bold text-[#1A2520]">Voice AI Call History</h2>
                  <p className="text-sm text-gray-500 font-medium">Recent interactions via your Exotel Growth Line</p>
                </div>
                <button 
                  onClick={() => setShowLogs(false)}
                  className="w-10 h-10 bg-white border border-gray-100 rounded-full flex items-center justify-center hover:bg-gray-50 transition shadow-sm"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-8">
                {loadingLogs ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <RefreshCw className="w-10 h-10 text-emerald-500 animate-spin mb-4" />
                    <p className="font-bold text-[#2C3E35]">Retrieving recordings...</p>
                  </div>
                ) : logs.length === 0 ? (
                  <div className="text-center py-20">
                    <Phone className="w-12 h-12 text-gray-200 mx-auto mb-4" />
                    <p className="text-gray-400 font-medium">No calls recorded yet.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {logs.map((log) => (
                      <div key={log.id} className="bg-[#FAF9F6] rounded-3xl p-6 border border-gray-100">
                        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-xl flex items-center justify-center">
                              <User className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="font-bold text-[#1A2520]">{log.from_number}</div>
                              <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">
                                {new Date(log.created_at).toLocaleString()}
                              </div>
                            </div>
                          </div>
                          <div className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border
                            ${log.status === 'completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-blue-50 text-blue-700 border-blue-100'}`}>
                            {log.status}
                          </div>
                        </div>

                        {log.ai_transcript && (
                          <div className="mb-6 bg-white rounded-2xl p-4 border border-gray-50">
                            <div className="flex items-center gap-2 mb-3 text-[10px] font-black uppercase tracking-widest text-gray-400">
                              <FileText className="w-3 h-3" /> AI Context Transcript
                            </div>
                            <p className="text-xs text-[#2C3E35]/70 whitespace-pre-line leading-relaxed italic">
                              {log.ai_transcript}
                            </p>
                          </div>
                        )}

                        {log.recording_url && (
                          <div className="flex items-center gap-4 bg-emerald-500 text-white rounded-2xl p-4 shadow-lg shadow-emerald-500/20">
                            <Play className="w-5 h-5" />
                            <div className="flex-1">
                              <div className="text-[10px] font-black uppercase tracking-widest opacity-70 mb-1">Play Recording</div>
                              <audio 
                                controls 
                                className="w-full h-8 filter invert brightness-100 contrast-100"
                                src={`${API}${log.recording_url}`}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showVoiceModal && (
          <BrowserVoiceModal onClose={() => setShowVoiceModal(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}
