import React, { useState } from 'react';
import { Upload, FileCode, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface Props {
  onUploadSuccess: () => void;
}

export const LogIngestionView: React.FC<Props> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.uploadLogs(formData);
      setResult(res.data);
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSample = async () => {
    const sampleLog = 
`[2026-10-27 10:15:32] [CRITICAL] [dns-pri] named[1042]: client @0x7f834c000c00 192.168.1.101#54122 (app.internal): query failed (SERVFAIL) for zone internal
[2026-10-27 10:15:35] [ERROR] [client-1] curl: (6) Could not resolve host: app.internal; DNS query timed out after 3000ms
[2026-10-27 10:15:42] [WARNING] [router-pri] kernel: GigabitEthernet0/1: carrier drop detected, interface transitioning to DOWN
[2026-10-27 10:15:48] [CRITICAL] [db-srv] postgres[8819]: [3-1] FATAL: remaining connection slots are reserved for non-replication superuser connections`;
    
    const blob = new Blob([sampleLog], { type: 'text/plain' });
    const sampleFile = new File([blob], 'network_incident_sample.log', { type: 'text/plain' });
    setFile(sampleFile);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-5">
      <div>
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <Upload className="w-5 h-5 text-cyan-400" />
          Network Log Ingestion &amp; Structured Parsing
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Upload syslog, JSON, JSONL, or CSV log streams. The parser normalizes events and populates the telemetry timeline.
        </p>
      </div>

      <form onSubmit={handleUpload} className="space-y-4">
        <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl p-6 text-center bg-slate-950/40">
          <FileCode className="w-8 h-8 mx-auto text-slate-500 mb-2" />
          <input
            type="file"
            accept=".log,.txt,.csv,.json,.jsonl"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-900/60 file:text-cyan-200 hover:file:bg-cyan-800/80 cursor-pointer"
          />
          {file && (
            <div className="mt-2 text-xs text-cyan-400 font-mono">
              Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!file || uploading}
            className="flex-1 py-2 px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium text-xs transition shadow-lg shadow-cyan-950/50"
          >
            {uploading ? 'Parsing Records...' : 'Upload & Parse Logs'}
          </button>
          <button
            type="button"
            onClick={handleLoadSample}
            className="py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 transition"
          >
            Load Synthetic Log Sample
          </button>
        </div>
      </form>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="w-4 h-4" /> Parsed successfully!
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
            <div>Records Parsed: <span className="font-mono text-cyan-400">{result.parsed_count}</span></div>
            <div>Rejected: <span className="font-mono text-rose-400">{result.rejected_count}</span></div>
          </div>
        </div>
      )}
    </div>
  );
};
