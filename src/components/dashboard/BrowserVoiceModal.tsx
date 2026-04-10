import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, X, Volume2, Loader2, Sparkles, MessageCircle } from 'lucide-react';

interface BrowserVoiceModalProps {
  onClose: () => void;
  salonId?: number;
}

export default function BrowserVoiceModal({ onClose, salonId = 1 }: BrowserVoiceModalProps) {
  const [status, setStatus] = useState<'idle' | 'connecting' | 'listening' | 'processing' | 'speaking' | 'error'>('connecting');
  const [transcript, setTranscript] = useState('');
  const [aiText, setAiText] = useState('');
  const [volume, setVolume] = useState(0);
  const [error, setError] = useState('');

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isSpeakingRef = useRef(false);

  // VAD Config (Optimized for 250ms)
  const SILENCE_THRESHOLD = 0.01;
  const SILENCE_DURATION = 250; // 0.25s of silence triggers processing

  useEffect(() => {
    initVoiceSession();
    return () => cleanup();
  }, []);

  const initVoiceSession = async () => {
    try {
      setStatus('connecting');
      
      // 1. Connect WebSocket
      const API_URL = 'localhost:8000'; // Hardcoded for simplicity as seen in api.ts
      const socket = new WebSocket(`ws://${API_URL}/ws/browser`);
      wsRef.current = socket;

      socket.onopen = () => {
        setupMicrophone();
      };

      socket.onmessage = async (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'audio') {
          playAudio(msg.data);
        } else if (msg.type === 'text') {
          setAiText(msg.data);
        } else if (msg.type === 'error') {
          setError(msg.message);
          setStatus('error');
        }
      };

      socket.onclose = () => setStatus('idle');
      socket.onerror = () => {
        setError('WebSocket Connection Failed');
        setStatus('error');
      };

    } catch (err: any) {
      setError(err.message || 'Initialization Failed');
      setStatus('error');
    }
  };

  const setupMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioContextClass({ sampleRate: 16000 });
      audioContextRef.current = ctx;

      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      source.connect(processor);
      processor.connect(ctx.destination);

      processor.onaudioprocess = (e: any) => {
        if (isSpeakingRef.current) return;

        const inputData = e.inputBuffer.getChannelData(0);
        
        // 1. Compute Volume for VAD
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        setVolume(rms);

        // 2. Send Raw PCM as Base64 to Backend
        // Convert Float32 to Int16
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcm16[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
        }
        const b64 = btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)));
        
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'audio', data: b64 }));
        }

        // 3. VAD Logic (Detect Silence)
        if (rms > SILENCE_THRESHOLD) {
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
          setStatus('listening');
        } else if (rms < SILENCE_THRESHOLD && !silenceTimerRef.current && status === 'listening') {
          silenceTimerRef.current = setTimeout(() => {
            triggerProcessing();
          }, SILENCE_DURATION);
        }
      };

    } catch (err: any) {
      setError('Microphone Access Denied');
      setStatus('error');
    }
  };

  const triggerProcessing = () => {
    setStatus('processing');
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'process' }));
    }
  };

  const playAudio = async (base64Audio: string) => {
    if (!audioContextRef.current) return;
    
    isSpeakingRef.current = true;
    setStatus('speaking');
    
    try {
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const pcm16 = new Int16Array(bytes.buffer);
      const float32 = new Float32Array(pcm16.length);
      for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 32768;
      }

      const audioBuffer = audioContextRef.current.createBuffer(1, float32.length, 24000);
      audioBuffer.getChannelData(0).set(float32);

      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      
      source.onended = () => {
        isSpeakingRef.current = false;
        setStatus('listening');
      };
      
      source.start();
    } catch (err) {
      console.error('Playback Error:', err);
      isSpeakingRef.current = false;
      setStatus('listening');
    }
  };

  const cleanup = () => {
    if (wsRef.current) wsRef.current.close();
    if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach(t => t.stop());
    if (audioContextRef.current) audioContextRef.current.close();
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
  };

  return (
    <div className="fixed inset-0 z-[150] flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="absolute inset-0 bg-[#1A2520]/80 backdrop-blur-md"
        onClick={onClose}
      />
      
      <motion.div 
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        className="relative w-full max-w-lg bg-white rounded-[3rem] shadow-2xl overflow-hidden border border-emerald-100"
      >
        {/* Header */}
        <div className="p-8 pb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-50 rounded-2xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h2 className="font-serif text-xl font-bold text-[#1A2520]">Agent Live Session</h2>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${status === 'listening' ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'}`} />
                <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">
                  {status}
                </span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-50 rounded-full transition">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Visualizer */}
        <div className="px-8 py-12 flex flex-col items-center">
          <div className="relative">
            <motion.div 
              animate={{ 
                scale: status === 'listening' ? [1, 1.2, 1] : 1,
                opacity: status === 'listening' ? [0.2, 0.4, 0.2] : 0.1
              }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="absolute inset-0 bg-emerald-500 rounded-full"
            />
            <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 shadow-xl overflow-hidden relative z-10
              ${status === 'listening' ? 'bg-emerald-500 text-white' : 
                status === 'speaking' ? 'bg-blue-500 text-white' : 
                status === 'processing' ? 'bg-amber-500 text-white' :
                'bg-gray-100 text-gray-400'}`}
            >
              {status === 'connecting' || status === 'processing' ? (
                <Loader2 className="w-10 h-10 animate-spin" />
              ) : status === 'speaking' ? (
                <Volume2 className="w-10 h-10 animate-bounce" />
              ) : (
                <Mic className="w-10 h-10" />
              )}
            </div>
          </div>

          <div className="mt-10 w-full h-1 bg-gray-50 rounded-full overflow-hidden">
             <motion.div 
               animate={{ width: `${Math.min(volume * 500, 100)}%` }}
               className="h-full bg-emerald-500"
             />
          </div>

          <div className="mt-8 text-center space-y-4 w-full">
            <AnimatePresence mode="wait">
              {aiText ? (
                <motion.div 
                  key="ai"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-emerald-50 p-6 rounded-[2rem] border border-emerald-100"
                >
                  <p className="text-sm font-semibold text-emerald-900 leading-relaxed italic">
                    "{aiText}"
                  </p>
                </motion.div>
              ) : (
                <motion.p 
                  key="hint"
                  className="text-gray-400 text-sm font-medium"
                >
                  {status === 'connecting' ? 'Initializing hardware...' : 
                   status === 'listening' ? 'Speak naturally, I am listening' :
                   status === 'processing' ? 'Thinking...' :
                   status === 'speaking' ? 'Responding...' : 'Waiting...'}
                </motion.p>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Footer */}
        <div className="p-8 bg-gray-50 flex items-center justify-center gap-4">
           {status === 'error' && (
             <p className="text-red-500 text-xs font-bold uppercase tracking-widest">{error}</p>
           )}
           <button 
             onClick={onClose}
             className="px-8 py-3 bg-[#1A2520] text-white rounded-2xl font-bold text-sm hover:shadow-lg transition shadow-emerald-900/10"
           >
             End Session
           </button>
        </div>
      </motion.div>
    </div>
  );
}
