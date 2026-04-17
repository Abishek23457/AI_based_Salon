"use client";
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Plus, Minus, Edit2, Trash2, Clock, UserCheck, AlertCircle } from 'lucide-react';
import { API_URL } from '../api';

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

export default function StaffManagement() {
  const [staff, setStaff] = useState<Staff[]>([]);
  const [stats, setStats] = useState<StaffStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [batchCount, setBatchCount] = useState(1);
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null);
  const [newStaff, setNewStaff] = useState({ name: '', working_hours: '9:00 AM - 6:00 PM' });

  useEffect(() => {
    fetchStaff();
    fetchStats();
  }, []);

  const fetchStaff = async () => {
    try {
      const response = await fetch(`${API_URL}/staff/`);
      const data = await response.json();
      setStaff(data);
    } catch {
      setError('Failed to fetch staff data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/staff/count');
      const data = await response.json();
      setStats(data);
    } catch {
      console.error('Failed to fetch staff stats');
    }
  };

  const handleAddStaff = async () => {
    if (!newStaff.name.trim()) return;
    
    try {
      const response = await fetch(`${API_URL}/staff/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newStaff),
      });
      
      if (response.ok) {
        setNewStaff({ name: '', working_hours: '9:00 AM - 6:00 PM' });
        fetchStaff();
        fetchStats();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to add staff');
      }
    } catch {
      setError('Failed to add staff');
    }
  };

  const handleUpdateStaff = async () => {
    if (!editingStaff) return;
    
    try {
      const response = await fetch(`http://localhost:8000/staff/${editingStaff.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editingStaff.name, working_hours: editingStaff.working_hours }),
      });
      
      if (response.ok) {
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
      const response = await fetch(`http://localhost:8000/staff/${id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        fetchStaff();
        fetchStats();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to delete staff');
      }
    } catch {
      setError('Failed to delete staff');
    }
  };

  const handleBatchUpdate = async (action: 'add' | 'remove') => {
    try {
      const response = await fetch('http://localhost:8000/staff/batch-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, count: batchCount }),
      });
      
      if (response.ok) {
        fetchStaff();
        fetchStats();
      } else {
        const error = await response.json();
        setError(error.detail || `Failed to ${action} staff`);
      }
    } catch {
      setError(`Failed to ${action} staff`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading staff management...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Staff Management</h1>
          <p className="text-gray-600">Manage your salon staff and optimize scheduling</p>
        </motion.div>

        {/* Stats Cards */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          >
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-emerald-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.total_count}</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800">Total Staff</h3>
              <p className="text-gray-600 text-sm mt-1">All team members</p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <UserCheck className="w-8 h-8 text-blue-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.active_count}</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800">Active Staff</h3>
              <p className="text-gray-600 text-sm mt-1">With upcoming bookings</p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <Clock className="w-8 h-8 text-amber-600" />
                <span className="text-3xl font-bold text-gray-900">{stats.available_count}</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800">Available</h3>
              <p className="text-gray-600 text-sm mt-1">Ready for appointments</p>
            </div>
          </motion.div>
        )}

        {/* Batch Operations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Operations</h2>
          
          <div className="flex flex-col md:flex-row gap-6">
            {/* Add Staff Batch */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Add Multiple Staff</label>
              <div className="flex gap-3">
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={batchCount}
                  onChange={(e) => setBatchCount(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
                <button
                  onClick={() => handleBatchUpdate('add')}
                  className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add Staff
                </button>
              </div>
            </div>

            {/* Remove Staff Batch */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Remove Staff</label>
              <div className="flex gap-3">
                <input
                  type="number"
                  min="1"
                  max={staff.length}
                  value={batchCount}
                  onChange={(e) => setBatchCount(Math.max(1, Math.min(staff.length, parseInt(e.target.value) || 1)))}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
                <button
                  onClick={() => handleBatchUpdate('remove')}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <Minus className="w-4 h-4" />
                  Remove Staff
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Add New Staff */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Add New Staff Member</h2>
          
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              placeholder="Staff Name"
              value={newStaff.name}
              onChange={(e) => setNewStaff({ ...newStaff, name: e.target.value })}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Working Hours"
              value={newStaff.working_hours}
              onChange={(e) => setNewStaff({ ...newStaff, working_hours: e.target.value })}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
            <button
              onClick={handleAddStaff}
              className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Staff
            </button>
          </div>
        </motion.div>

        {/* Staff List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden"
        >
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900">Current Staff Members</h2>
          </div>
          
          <div className="divide-y divide-gray-100">
            {staff.map((member, index) => (
              <motion.div
                key={member.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                {editingStaff?.id === member.id ? (
                  <div className="flex flex-col md:flex-row gap-4">
                    <input
                      type="text"
                      value={editingStaff.name}
                      onChange={(e) => setEditingStaff({ ...editingStaff, name: e.target.value })}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    />
                    <input
                      type="text"
                      value={editingStaff.working_hours}
                      onChange={(e) => setEditingStaff({ ...editingStaff, working_hours: e.target.value })}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleUpdateStaff}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingStaff(null)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-emerald-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{member.name}</h3>
                        <p className="text-gray-600 flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          {member.working_hours}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setEditingStaff(member)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteStaff(member.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
            
            {staff.length === 0 && (
              <div className="p-12 text-center">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No staff members yet. Add your first team member above.</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 right-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 max-w-md"
          >
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800 text-sm">{error}</p>
            <button
              onClick={() => setError('')}
              className="text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
