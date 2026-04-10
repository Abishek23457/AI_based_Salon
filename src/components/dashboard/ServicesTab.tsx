import React from 'react';
import { PlusCircle, Clock, Trash2 } from 'lucide-react';

export default function ServicesTab({ services, svcForm, setSvcForm, addService, deleteService }: any) {
  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-[#1A2520] font-serif">Service Catalog</h1>

      {/* Add New Service Form */}
      <form onSubmit={addService} className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-2 h-full bg-[#4A6B53]"/>
        <h3 className="font-bold text-[#2C3E35] mb-6 flex items-center gap-2"><PlusCircle className="w-5 h-5" /> Add New Service</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <input required placeholder="Service name" value={svcForm.name} onChange={e => setSvcForm({ ...svcForm, name: e.target.value })}
            className="col-span-2 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input required type="number" placeholder="Price (₹)" value={svcForm.price} onChange={e => setSvcForm({ ...svcForm, price: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input required type="number" placeholder="Duration (min)" value={svcForm.duration_minutes} onChange={e => setSvcForm({ ...svcForm, duration_minutes: e.target.value })}
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
          <input placeholder="Short description (optional)" value={svcForm.description} onChange={e => setSvcForm({ ...svcForm, description: e.target.value })}
            className="col-span-4 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-[#4A6B53] font-medium" />
        </div>
        <button type="submit" className="mt-6 px-8 py-3 bg-[#2C3E35] text-white rounded-xl font-bold hover:bg-[#1A2520] transition shadow-md">Add Service</button>
      </form>

      {/* Service List Table */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {['Service', 'Price', 'Duration', 'Description', ''].map(h => (
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
