import React, { useState, useEffect } from 'react';
import { PlusCircle, Clock, Trash2, User, Edit2, Save, X, ChevronDown } from 'lucide-react';
import { API_URL as API } from '../../api';

export default function ServicesTab({ services, svcForm, setSvcForm, addService, deleteService, salonId, authFetch, showToast }: any) {
  const [staff, setStaff] = useState<any[]>([]);
  const [serviceStaffAssignments, setServiceStaffAssignments] = useState<Record<number, number[]>>({});
  const [editingServiceStaff, setEditingServiceStaff] = useState<number | null>(null);
  const [selectedStaffIds, setSelectedStaffIds] = useState<number[]>([]);
  const [newServiceStaffIds, setNewServiceStaffIds] = useState<number[]>([]);
  const [selectedPresetService, setSelectedPresetService] = useState('');

  const predefinedServices = [
    { name: "Haircut", price: "500", duration_minutes: "30", description: "Classic haircut with wash and styling" },
    { name: "Hair Coloring", price: "2000", duration_minutes: "90", description: "Full hair coloring with premium products" },
    { name: "Facial", price: "1500", duration_minutes: "60", description: "Deep cleansing facial treatment" },
    { name: "Manicure", price: "800", duration_minutes: "45", description: "Professional manicure with nail care" },
    { name: "Pedicure", price: "800", duration_minutes: "45", description: "Relaxing pedicure with foot massage" },
    { name: "Massage", price: "1800", duration_minutes: "60", description: "Full body aromatherapy massage" },
    { name: "Bridal Makeup", price: "5000", duration_minutes: "120", description: "Complete bridal makeup package" },
    { name: "Hair Styling", price: "700", duration_minutes: "45", description: "Professional hair styling for events" },
    { name: "Waxing", price: "600", duration_minutes: "30", description: "Full body waxing service" },
    { name: "Keratin Treatment", price: "3500", duration_minutes: "120", description: "Hair smoothing keratin treatment" }
  ];

  const handlePresetServiceChange = (serviceName: string) => {
    setSelectedPresetService(serviceName);
    const preset = predefinedServices.find(s => s.name === serviceName);
    if (preset) {
      setSvcForm({ ...svcForm, name: preset.name, price: preset.price, duration_minutes: preset.duration_minutes, description: preset.description });
    }
  };

  useEffect(() => {
    const fetchStaff = async () => {
      try {
        const response = await authFetch(`${API}/staff/?salon_id=${salonId}`);
        const data = await response.json();
        setStaff(data);
      } catch (err) {
        console.error('Failed to fetch staff:', err);
      }
    };
    fetchStaff();
  }, [authFetch, salonId]);

  const handleAssignStaff = (serviceId: number) => {
    setServiceStaffAssignments(prev => ({
      ...prev,
      [serviceId]: selectedStaffIds
    }));
    setEditingServiceStaff(null);
    setSelectedStaffIds([]);
    showToast(`Staff assigned to service`);
  };

  const toggleStaffSelection = (staffId: number) => {
    setSelectedStaffIds(prev => 
      prev.includes(staffId) 
        ? prev.filter(id => id !== staffId)
        : [...prev, staffId]
    );
  };

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-[#1A2520] font-serif">Service Catalog</h1>

      {/* Add New Service Form */}
      <form onSubmit={(e) => { e.preventDefault(); addService(e, newServiceStaffIds); setNewServiceStaffIds([]); setSelectedPresetService(''); }} className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-2 h-full bg-[#4A6B53]"/>
        <h3 className="font-bold text-[#2C3E35] mb-6 flex items-center gap-2"><PlusCircle className="w-5 h-5" /> Add New Service</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Predefined Services Dropdown */}
          <div className="col-span-4 mb-2">
            <label className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2 block">Select Predefined Service (Optional)</label>
            <select 
              value={selectedPresetService}
              onChange={e => handlePresetServiceChange(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium"
            >
              <option value="">-- Select a predefined service --</option>
              {predefinedServices.map(service => (
                <option key={service.name} value={service.name}>
                  {service.name} - ₹{service.price} ({service.duration_minutes} min)
                </option>
              ))}
            </select>
          </div>
          
          <input required placeholder="Service name" value={svcForm.name} onChange={e => setSvcForm({ ...svcForm, name: e.target.value })}
            className="col-span-2 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input required type="number" placeholder="Price (₹)" value={svcForm.price} onChange={e => setSvcForm({ ...svcForm, price: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input required type="number" placeholder="Duration (min)" value={svcForm.duration_minutes} onChange={e => setSvcForm({ ...svcForm, duration_minutes: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input placeholder="Short description (optional)" value={svcForm.description} onChange={e => setSvcForm({ ...svcForm, description: e.target.value })}
            className="col-span-4 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          
          {/* Staff Selection */}
          <div className="col-span-4 mt-2">
            <label className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2 block">Assign Staff (Optional)</label>
            <div className="flex flex-wrap gap-2">
              {staff.length === 0 ? (
                <p className="text-gray-400 text-xs">No staff available. Add staff first.</p>
              ) : (
                staff.map((staffMember: any) => (
                  <label key={staffMember.id} className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition">
                    <input 
                      type="checkbox" 
                      checked={newServiceStaffIds.includes(staffMember.id)}
                      onChange={() => {
                        setNewServiceStaffIds(prev => 
                          prev.includes(staffMember.id) 
                            ? prev.filter(id => id !== staffMember.id)
                            : [...prev, staffMember.id]
                        );
                      }}
                      className="rounded text-emerald-600"
                    />
                    <span className="text-xs font-medium">{staffMember.name}</span>
                  </label>
                ))
              )}
            </div>
          </div>
        </div>
        <button type="submit" className="mt-6 px-8 py-3 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-md">Add Service</button>
      </form>

      {/* Service List Table */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {['Service', 'Price', 'Duration', 'Assigned Staff', 'Description', 'Actions'].map(h => (
                <th key={h} className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-gray-400">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {services.map((s: any) => (
              <tr key={s.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50/60 transition">
                <td className="px-6 py-4 font-bold text-[#2C3E35]">{s.name}</td>
                <td className="px-6 py-4 font-semibold text-emerald-700">₹{s.price}</td>
                <td className="px-6 py-4 text-gray-500 flex items-center gap-1"><Clock className="w-3 h-3" /> {s.duration_minutes} min</td>
                <td className="px-6 py-4">
                  {editingServiceStaff === s.id ? (
                    <div className="relative">
                      <button 
                        onClick={() => setEditingServiceStaff(null)}
                        className="flex items-center gap-2 px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 font-bold text-xs"
                      >
                        <X className="w-3 h-3" /> Cancel
                      </button>
                      <div className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-xl p-3 z-10 w-64 max-h-48 overflow-y-auto">
                        {staff.length === 0 ? (
                          <p className="text-gray-400 text-xs text-center py-2">No staff available</p>
                        ) : (
                          staff.map((staffMember: any) => (
                            <label key={staffMember.id} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                              <input 
                                type="checkbox" 
                                checked={selectedStaffIds.includes(staffMember.id)}
                                onChange={() => toggleStaffSelection(staffMember.id)}
                                className="rounded text-emerald-600"
                              />
                              <span className="text-xs font-medium">{staffMember.name}</span>
                            </label>
                          ))
                        )}
                        <button 
                          onClick={() => handleAssignStaff(s.id)}
                          className="w-full mt-2 py-2 bg-emerald-600 text-white rounded-lg font-bold text-xs hover:bg-emerald-700"
                        >
                          Save Assignments
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button 
                      onClick={() => {
                        setEditingServiceStaff(s.id);
                        setSelectedStaffIds(serviceStaffAssignments[s.id] || []);
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 rounded-lg text-gray-600 text-xs font-bold hover:bg-gray-200 transition"
                    >
                      <User className="w-3 h-3" /> 
                      {serviceStaffAssignments[s.id]?.length > 0 
                        ? `${serviceStaffAssignments[s.id].length} staff` 
                        : 'Assign Staff'}
                    </button>
                  )}
                </td>
                <td className="px-6 py-4 text-gray-400 text-xs truncate max-w-[200px]">{s.description || '—'}</td>
                <td className="px-6 py-4"><button onClick={() => deleteService(s.id)} className="text-red-400 hover:text-red-600 transition"><Trash2 className="w-4 h-4" /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
