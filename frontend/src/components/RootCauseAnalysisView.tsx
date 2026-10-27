import React, { useState } from 'react';
import { 
  FileText, 
  Bot, 
  CheckCircle, 
  Sparkles, 
  Send 
} from 'lucide-react';
import { Incident, api } from '../services/api';

interface Props {
  incidents: Incident[];
  onRefresh: () => void;
}

export const RootCauseAnalysisView: React.FC<Props> = ({ incidents, onRefresh }) => {
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(incidents[0] || null);
  const [aiExplanation, setAiExplanation] = useState<string>('');
  const [chatQuestion, setChatQuestion] = useState<string>('');
  const [chatAnswer, setChatAnswer] = useState<string>('');
  const [loadingAi, setLoadingAi] = useState(false);
  const [feedbackNotes, setFeedbackNotes] = useState('');
  const [feedbackSaved, setFeedbackSaved] = useState(false);

  const activeInc = selectedIncident || incidents[0];

  const handleExplain = async () => {
    if (!activeInc) return;
    setLoadingAi(true);
    try {
      const res = await api.explainIncident(activeInc.id);
      setAiExplanation(res.data.explanation);
    } catch (e: any) {
      setAiExplanation(`Explanation error: ${e.message}`);
    } finally {
      setLoadingAi(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuestion.trim()) return;
    try {
      const res = await api.chatAssistant(chatQuestion, activeInc?.id);
      setChatAnswer(res.data.answer);
    } catch (e: any) {
      setChatAnswer(`Error: ${e.message}`);
    }
  };

  const handleVerify = async (status: string) => {
    if (!activeInc) return;
    try {
      await api.submitFeedback(activeInc.id, {
        confirmed_root_cause: activeInc.suspected_root_cause,
        actual_recovery_taken: activeInc.recommended_recovery,
        feedback_notes: feedbackNotes || 'Verified by Network Operations Engineer.',
        status: status
      });
      setFeedbackSaved(true);
      setTimeout(() => setFeedbackSaved(false), 3000);
      onRefresh();
    } catch (e: any) {
      alert(`Error submitting feedback: ${e.message}`);
    }
  };

  if (!activeInc) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
        <FileText className="w-10 h-10 mx-auto text-slate-600 mb-2" />
        <p className="text-sm">No incidents recorded yet. Inject a fault scenario from the Fault Simulator to trigger an automated Root-Cause Analysis.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Incidents Sidebar List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
        <h3 className="text-sm font-semibold text-slate-200">Detected Incidents ({incidents.length})</h3>
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {incidents.map((inc) => (
            <button
              key={inc.id}
              onClick={() => {
                setSelectedIncident(inc);
                setAiExplanation('');
                setChatAnswer('');
              }}
              className={`w-full text-left p-3 rounded-lg border transition ${
                activeInc.id === inc.id
                  ? 'bg-cyan-950/40 border-cyan-700/60 text-slate-100'
                  : 'bg-slate-950/60 border-slate-800/80 text-slate-400 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="font-mono text-cyan-400">{inc.id}</span>
                <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">{inc.category}</span>
              </div>
              <div className="text-xs font-medium text-slate-200 line-clamp-1">{inc.title}</div>
              <div className="text-[10px] text-slate-500 mt-1">Confidence: {Math.round(inc.confidence_score * 100)}%</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main RCA Detail Report */}
      <div className="lg:col-span-2 space-y-5">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-start justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs px-2 py-0.5 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded">
                  {activeInc.id}
                </span>
                <span className="text-xs px-2 py-0.5 bg-rose-950 text-rose-400 border border-rose-800 rounded">
                  {activeInc.severity}
                </span>
                <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                  Status: {activeInc.status}
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-100">{activeInc.title}</h2>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400">Deterministic Confidence</span>
              <div className="text-lg font-mono font-bold text-cyan-400">
                {Math.round(activeInc.confidence_score * 100)}%
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Suspected Root Cause</h4>
            <p className="text-sm font-medium text-slate-100 bg-slate-950 p-3 rounded-lg border border-slate-800">
              {activeInc.suspected_root_cause}
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Supporting Evidence</h4>
            <div className="space-y-1.5">
              {activeInc.evidences.map((ev, i) => (
                <div key={i} className="text-xs bg-slate-950/80 p-2.5 rounded border border-slate-800/80 flex items-start gap-2">
                  <span className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-cyan-300 uppercase">
                    {ev.evidence_type}
                  </span>
                  <span className="text-slate-300">{ev.description}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Impacted Nodes</span>
              <span className="font-mono text-rose-300">{activeInc.affected_nodes.join(', ') || 'None'}</span>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Affected Services</span>
              <span className="font-mono text-amber-300">{activeInc.affected_services.join(', ') || 'None'}</span>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Recommended Recovery Strategy</h4>
            <p className="text-xs text-emerald-400 bg-emerald-950/30 border border-emerald-800/50 p-3 rounded-lg">
              {activeInc.recommended_recovery}
            </p>
          </div>

          {/* Verification & Memory Feedback */}
          <div className="border-t border-slate-800 pt-3">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Administrator Ground-Truth Feedback</h4>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Optional verification notes for historical memory..."
                value={feedbackNotes}
                onChange={(e) => setFeedbackNotes(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200"
              />
              <button
                onClick={() => handleVerify('confirmed')}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white font-medium transition"
              >
                <CheckCircle className="w-3.5 h-3.5" /> Confirm
              </button>
            </div>
            {feedbackSaved && (
              <p className="text-[11px] text-emerald-400 mt-1">Confirmed root cause recorded into verified incident memory.</p>
            )}
          </div>
        </div>

        {/* AI Natural Language Assistant Box */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <Bot className="w-4 h-4 text-cyan-400" /> AI Diagnostic Copilot (Evidence Grounded)
            </h3>
            <button
              onClick={handleExplain}
              disabled={loadingAi}
              className="flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg bg-cyan-700/60 hover:bg-cyan-600/80 text-cyan-100 border border-cyan-600 transition"
            >
              <Sparkles className="w-3.5 h-3.5" /> {loadingAi ? 'Generating...' : 'Explain Incident in Plain Language'}
            </button>
          </div>

          {aiExplanation && (
            <div className="text-xs bg-slate-950 p-4 rounded-lg border border-slate-800 whitespace-pre-line text-slate-300 leading-relaxed">
              {aiExplanation}
            </div>
          )}

          <form onSubmit={handleChat} className="flex gap-2">
            <input
              type="text"
              placeholder="Ask a technical question about this incident..."
              value={chatQuestion}
              onChange={(e) => setChatQuestion(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs flex items-center gap-1 border border-slate-700 transition"
            >
              <Send className="w-3.5 h-3.5" /> Ask
            </button>
          </form>

          {chatAnswer && (
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300">
              <span className="font-semibold text-cyan-400">Copilot Answer: </span>
              {chatAnswer}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
