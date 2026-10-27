import React, { useState } from 'react';
import { History, Search, CheckCircle2, ChevronRight, BookOpen } from 'lucide-react';
import { Incident } from '../services/api';

interface Props {
  incidents: Incident[];
  onSelectIncident: (inc: Incident) => void;
}

export const IncidentHistoryView: React.FC<Props> = ({ incidents, onSelectIncident }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const filtered = incidents.filter((inc) => {
    const matchesSearch = inc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          inc.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          inc.suspected_root_cause.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'ALL' || inc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = ['ALL', ...Array.from(new Set(incidents.map((i) => i.category)))];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" />
            Incident Memory &amp; Historical Ground Truth
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit past failure events, administrator-verified root causes, and verified recovery outcomes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search past incidents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border border-slate-800 rounded-lg">
          <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3">Incident ID</th>
              <th className="py-2.5 px-3">Timestamp</th>
              <th className="py-2.5 px-3">Title &amp; Root Cause</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-6 text-center text-slate-500">
                  No historical incidents matched your query.
                </td>
              </tr>
            ) : (
              filtered.map((inc) => (
                <tr key={inc.id} className="hover:bg-slate-800/40">
                  <td className="py-2.5 px-3 font-mono text-cyan-400">{inc.id}</td>
                  <td className="py-2.5 px-3 text-slate-400 font-mono">
                    {new Date(inc.created_at).toLocaleDateString()} {new Date(inc.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="font-semibold text-slate-200">{inc.title}</div>
                    <div className="text-[11px] text-slate-400 line-clamp-1">{inc.suspected_root_cause}</div>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                      {inc.category}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      inc.status === 'confirmed' 
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                        : 'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}>
                      {inc.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-cyan-400 font-semibold">
                    {Math.round(inc.confidence_score * 100)}%
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => onSelectIncident(inc)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs inline-flex items-center gap-1 border border-slate-700 transition"
                    >
                      Inspect <ChevronRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
