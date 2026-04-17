import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Plus, Minus, Edit2, Trash2, Clock, UserCheck, AlertCircle, Phone } from 'lucide-react';
import { API_URL as API } from '../../api';

interface Staff {
  id: number;
  name: string;
  working_hours: string;
}

interface StaffStats {
  total_count: number;
  active_count: number;
  available_count: number;
}

export default function StaffTab({ salonId, authFetch, showToast }: any) {
  const [staff, setStaff] = useState<Staff[]>([]);
  const [stats, setStats] = useState<StaffStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [batchCount, setBatchCount] = useState(1);
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null);
  const [newStaff, setNewStaff] = useState({ name: '', working_hours: '9:00 AM - 6:00 PM' });

  const fetchStaff = useCallback(async () => {
    try {
      const response = await authFetch(`${API}/staff/?salon_id=${salonId}`);
      const data = await response.json();
      setStaff(data);
    } catch {
      setError('Failed to fetch staff data');
    } finally {
      setLoading(false);
    }
  }, [authFetch, salonId]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await authFetch(`${API}/staff/count?salon_id=${salonId}`);
      const data = await response.json();
      setStats(data);
    } catch {
      console.error('Failed to fetch staff stats');
    }
  }, [authFetch, salonId]);

  useEffect(() => {
    fetchStaff();
    fetchStats();
  }, [fetchStaff, fetchStats]);

  const handleAddStaff = async () => {
    if (!newStaff.name.trim()) return;
    
    try {
      const response = await authFetch(`${API}/staff/?salon_id=${salonId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newStaff),
      });
      
      if (response.ok) {
        showToast('Staff member added ✓');
        setNewStaff({ name: '', working_hours: '9:00 AM - 6:00 PM' });
        fetchStaff();
        fetchStats();
      } else {
        const err = await response.json();
        setError(err.detail || 'Failed to add staff');
      }
    } catch {
      setError('Failed to add staff');
    }
  };

  const handleUpdateStaff = async () => {
    if (!editingStaff) return;
    
    try {
      const response = await authFetch(`${API}/staff/${editingStaff.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editingStaff.name, working_hours: editingStaff.working_hours }),
      });
      
      if (response.ok) {
        showToast('Staff member updated ✓');
        setEditingStaff(null);
        fetchStaff();
      } else {
        setError('Failed to update staff');
      }
    } catch {
      setError('Failed to update staff');
    }
  };

  const handleDeleteStaff = async (id: number) => {
    try {
      const response = await authFetch(`${API}/staff/${id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        showToast('Staff member removed');
        fetchStaff();
        fetchStats();
      } else {
        const err = await response.json();
        setError(err.detail || 'Failed to delete staff');
      }
    } catch {
      setError('Failed to delete staff');
    }
  };

  if (loading) return <div className="py-20 text-center text-gray-400 font-medium animate-pulse">Loading Staff Management...</div>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-bold text-[#1A2520] font-serif">Staff Management</h1>
        <div className="bg-emerald-50 px-4 py-2 rounded-xl border border-emerald-100 flex items-center gap-2">
            <Phone className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-bold text-emerald-800 uppercase tracking-widest">Active Operations</span>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-400">Total Staff</span>
              <Users className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-3xl font-bold text-[#1A2520]">{stats.total_count}</p>
          </div>
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-400">Active Duty</span>
              <UserCheck className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-[#1A2520]">{stats.active_count}</p>
          </div>
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-400">Available</span>
              <Clock className="w-5 h-5 text-amber-600" />
            </div>
            <p className="text-3xl font-bold text-[#1A2520]">{stats.available_count}</p>
          </div>
        </div>
      )}

      {/* Add New Staff */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-2 h-full bg-[#4A6B53]"/>
        <h3 className="font-bold text-[#2C3E35] mb-6 flex items-center gap-2 font-serif text-xl">
            <Plus className="w-5 h-5 text-emerald-600" /> Hire New Member
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input required placeholder="Staff Full Name" value={newStaff.name} onChange={e => setNewStaff({ ...newStaff, name: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input required placeholder="Working Hours (e.g. 9AM–6PM)" value={newStaff.working_hours} onChange={e => setNewStaff({ ...newStaff, working_hours: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
        </div>
        <button onClick={handleAddStaff} className="mt-6 px-8 py-3 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-md">
            Add to Team
        </button>
      </div>

      {/* Staff List */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {['Team Member', 'Activity Hours', 'Action'].map(h => (
                <th key={h} className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-gray-400">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {staff.length === 0 ? (
                <tr><td colSpan={3} className="text-center py-16 text-gray-400 font-medium">No staff members assigned yet.</td></tr>
            ) : staff.map(member => (
              <tr key={member.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50/60 transition group">
                <td className="px-6 py-4">
                  {editingStaff?.id === member.id ? (
                    <input value={editingStaff.name} onChange={e => setEditingStaff({ ...editingStaff, name: e.target.value })}
                      className="px-3 py-1 border border-gray-200 rounded-lg outline-none focus:ring-1 focus:ring-emerald-500 font-bold" />
                  ) : (
                    <div className="font-bold text-[#2C3E35]">{member.name}</div>
                  )}
                </td>
                <td className="px-6 py-4">
                  {editingStaff?.id === member.id ? (
                    <input value={editingStaff.working_hours} onChange={e => setEditingStaff({ ...editingStaff, working_hours: e.target.value })}
                      className="px-3 py-1 border border-gray-200 rounded-lg outline-none focus:ring-1 focus:ring-emerald-500 text-sm" />
                  ) : (
                    <div className="text-gray-500 flex items-center gap-1.5 font-medium"><Clock className="w-3 h-3" /> {member.working_hours}</div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-4">
                    {editingStaff?.id === member.id ? (
                      <div className="flex gap-2">
                        <button onClick={handleUpdateStaff} className="text-emerald-600 font-bold text-xs uppercase tracking-widest hover:underline">Save</button>
                        <button onClick={() => setEditingStaff(null)} className="text-gray-400 font-bold text-xs uppercase tracking-widest hover:underline">Cancel</button>
                      </div>
                    ) : (
                      <>
                        <button onClick={() => setEditingStaff(member)} className="text-blue-400 hover:text-blue-600 transition"><Edit2 className="w-4 h-4"/></button>
                        <button onClick={() => handleDeleteStaff(member.id)} className="text-red-400 hover:text-red-600 transition"><Trash2 className="w-4 h-4"/></button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {error && (
        <div className="fixed bottom-24 right-6 animate-bounce bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3 shadow-xl z-50">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-800 text-xs font-bold">{error}</p>
          <button onClick={() => setError('')} className="text-red-600 text-sm font-black">&times;</button>
        </div>
      )}
    </div>
  );
}
