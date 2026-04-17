"use client";
import React, { useState } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import { API_URL } from '../api';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user'|'ai', content: string}[]>([
    { role: 'ai', content: 'Hi there! I am the BookSmart AI Receptionist. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');

  // Test function to verify chat is working
  const testConnection = async () => {
    try {
      console.log('Testing chat connection...');
      const response = await fetch(`${API_URL}/intelligent-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: 'hello test',
          customer_name: 'Test User'
        })
      });
      
      const data = await response.json();
      console.log('Test response:', data);
      alert('Chat is working! Response: ' + data.response);
    } catch (error) {
      console.error('Test failed:', error);
      alert('Chat test failed: ' + (error as Error).message);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');

    try {
      console.log('Sending message:', userMsg);
      // Use fallback chat receptionist endpoint
      const response = await fetch(`${API_URL}/chat-receptionist/receptionist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMsg,
          customer_name: "Customer"
        })
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      setMessages(prev => [...prev, { role: 'ai', content: data.ai_response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I'm having trouble connecting. Please try again or call us at +91-9876543210 for immediate assistance." }]);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100]">
      {!isOpen ? (
        <button 
          key="chat-toggle"
          onClick={() => setIsOpen(true)}
          className="w-16 h-16 bg-[#2C3E35] rounded-full flex items-center justify-center text-[#FAF9F6] shadow-2xl hover:scale-105 transition"
        >
          <MessageCircle className="w-8 h-8" />
        </button>
      ) : (
        <div className="w-80 md:w-96 bg-white rounded-3xl shadow-2xl border border-gray-100 flex flex-col h-[500px] overflow-hidden">
          <div className="bg-[#2C3E35] text-white p-4 flex justify-between items-center rounded-t-3xl">
            <div>
              <h3 className="font-bold text-lg">Growth Assistant</h3>
              <p className="text-sm font-medium">Direct line: 9513886363</p>
            </div>
            <button 
              key="chat-close"
              onClick={() => setIsOpen(false)} 
              className="hover:opacity-70 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#FAF9F6]">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-3 rounded-2xl max-w-[80%] text-sm ${msg.role === 'user' ? 'bg-[#4A6B53] text-white rounded-tr-sm' : 'bg-white border border-gray-100 shadow-sm rounded-tl-sm text-[#2C3E35]'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={sendMessage} className="p-4 bg-white border-t border-gray-100 flex items-center gap-2">
            <input 
              type="text" 
              value={input}
              onChange={e => setInput(e.target.value)}
              className="flex-1 px-4 py-2 bg-[#FAF9F6] border border-gray-200 rounded-full focus:outline-none focus:ring-1 focus:ring-[#4A6B53] transition text-sm text-[#2C3E35]"
              placeholder="Ask about prices, slots..."
            />
            <button 
              key="chat-send"
              type="submit" 
              className="w-10 h-10 bg-[#2C3E35] rounded-full flex items-center justify-center text-white hover:bg-[#1A2520] transition shrink-0"
            >
              <Send className="w-4 h-4 ml-[2px]" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
