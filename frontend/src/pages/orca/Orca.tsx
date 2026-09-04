import { useState } from "react";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Compass,
  Loader2,
  MapPin,
  MessageCircle,
  Send,
  Thermometer,
  Waves,
  Wind,
} from "lucide-react";
import { useOrca } from "../../hooks/useOrca";
import type { OrcaEvidence, OrcaResponse } from "../../types/orca";

interface ConditionCardProps {
  label: string;
  value: string;
  unit?: string;
  icon: React.ReactNode;
}

function ConditionCard({
  label,
  value,
  unit,
  icon,
}: ConditionCardProps): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold text-white">
            {value}
            {unit && <span className="ml-1 text-sm font-normal text-slate-400">{unit}</span>}
          </p>
        </div>
        <div className="rounded-xl bg-slate-700 p-3 text-cyan-400">{icon}</div>
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (value == null) return "—";

  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function getEvidenceList(response: OrcaResponse | undefined): OrcaEvidence[] {
  if (!response || !Array.isArray(response.evidence)) return [];
  return response.evidence;
}

export default function Orca(): React.JSX.Element {
  const [query, setQuery] = useState("");
  const orca = useOrca();
  const result = orca.data;
  const evidence = getEvidenceList(result);

  const handleAsk = (): void => {
    const trimmed = query.trim();
    if (!trimmed || orca.isPending) return;

    orca.mutate({
      query: trimmed,
      language: "en",
    });
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>): void => {
    if (event.key === "Enter") handleAsk();
  };

  const recommendation = result?.recommendation;
  const risk = result?.risk;
  const riskObject = typeof risk === "object" && risk !== null ? risk : undefined;
  const riskFactors = Array.isArray(riskObject?.factors) ? riskObject.factors : [];

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400">
              <Bot size={30} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">ORCA Assistant</h1>
              <p className="mt-1 text-sm text-slate-400">
                Ocean Research & Catch Advisory
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start rounded-full border border-green-500/20 bg-green-500/10 px-4 py-2 text-sm font-medium text-green-400 md:self-auto">
          <span className="h-2 w-2 rounded-full bg-green-400" />
          Ready
        </div>
      </div>

      {/* ASK ORCA */}
      <section className="rounded-2xl border border-cyan-500/20 bg-slate-800 p-6 shadow-lg shadow-cyan-950/10">
        <div className="flex items-center gap-2 text-white">
          <MessageCircle size={20} className="text-cyan-400" />
          <h2 className="text-xl font-semibold">Ask ORCA</h2>
        </div>
        <p className="mt-2 text-sm text-slate-400">
          Ask about ocean conditions, fishing suitability, safety, or marine observations.
        </p>

        <div className="mt-5 flex flex-col gap-3 md:flex-row">
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Is it safe to go fishing near Mumbai tomorrow?"
            className="min-w-0 flex-1 rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-cyan-400"
          />
          <button
            type="button"
            onClick={handleAsk}
            disabled={!query.trim() || orca.isPending}
            className="flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {orca.isPending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            {orca.isPending ? "Thinking..." : "Ask ORCA"}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {[
            "Fishing conditions near Mumbai",
            "Ocean safety tomorrow",
            "Best conditions for fishing",
          ].map((question) => (
            <button
              key={question}
              type="button"
              onClick={() => setQuery(question)}
              className="rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 transition hover:border-cyan-500/50 hover:text-cyan-300"
            >
              {question}
            </button>
          ))}
        </div>
      </section>

      {/* CURRENT ORCA RESPONSE */}
      <section className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-cyan-500/10 p-2 text-cyan-400">
            <Bot size={22} />
          </div>
          <div>
            <h2 className="font-semibold text-white">ORCA Recommendation</h2>
            <p className="text-xs text-slate-500">
              {orca.isPending ? "Analyzing your request" : result ? "Latest ORCA response" : "Waiting for your question"}
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-slate-700 bg-slate-900/60 p-6">
          {orca.isPending && (
            <div className="flex flex-col items-center justify-center text-center">
              <Loader2 size={32} className="animate-spin text-cyan-400" />
              <p className="mt-3 text-slate-300">ORCA is analyzing ocean conditions...</p>
              <p className="mt-1 text-xs text-slate-600">This may take a few moments.</p>
            </div>
          )}

          {orca.isError && !orca.isPending && (
            <div className="text-center">
              <AlertTriangle size={32} className="mx-auto text-amber-400" />
              <p className="mt-3 text-slate-300">Unable to reach ORCA right now.</p>
              <p className="mt-1 text-xs text-slate-500">
                {orca.error instanceof Error ? orca.error.message : "Please try again."}
              </p>
            </div>
          )}

          {!orca.isPending && !orca.isError && result && (
            <div className="whitespace-pre-wrap text-sm leading-6 text-slate-200">
              {result.response ?? result.answer ?? "ORCA returned no response."}
            </div>
          )}

          {!orca.isPending && !orca.isError && !result && (
            <div className="text-center">
              <Compass size={32} className="mx-auto text-slate-600" />
              <p className="mt-3 text-slate-400">
                Ask ORCA a question to generate an ocean intelligence recommendation.
              </p>
              <p className="mt-1 text-xs text-slate-600">
                The backend response will appear here after you submit a query.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* ENVIRONMENT SNAPSHOT */}
      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-white">Environment Snapshot</h2>
          <p className="mt-1 text-sm text-slate-400">
            Environmental evidence returned by ORCA for the latest query.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <ConditionCard
            label="Sea Temperature"
            value="—"
            unit="°C"
            icon={<Thermometer size={22} />}
          />
          <ConditionCard
            label="Wave Height"
            value="—"
            unit="m"
            icon={<Waves size={22} />}
          />
          <ConditionCard
            label="Wind Speed"
            value="—"
            unit="m/s"
            icon={<Wind size={22} />}
          />
          <ConditionCard
            label="Location"
            value="—"
            icon={<MapPin size={22} />}
          />
        </div>

        {evidence.length > 0 && (
          <div className="mt-4 rounded-2xl border border-slate-700 bg-slate-800 p-5">
            <h3 className="font-semibold text-white">Evidence Returned by ORCA</h3>
            <div className="mt-4 space-y-3">
              {evidence.map((item, index) => (
                <div key={`${item.metric ?? item.source ?? "evidence"}-${index}`} className="rounded-xl bg-slate-900/70 p-4">
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    {item.metric && <span className="font-medium text-cyan-300">{item.metric}</span>}
                    {item.value != null && <span className="text-white">{formatValue(item.value)}</span>}
                    {item.unit && <span className="text-slate-500">{item.unit}</span>}
                  </div>
                  {item.source && <p className="mt-1 text-xs text-slate-500">Source: {item.source}</p>}
                  {item.timestamp && <p className="mt-1 text-xs text-slate-600">Time: {item.timestamp}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* DECISION PANEL */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-green-500/20 bg-green-950/10 p-6">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="text-green-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Fishing Suitability</h2>
          </div>
          <p className="mt-4 text-slate-400">
            ORCA combines available environmental indicators to support the fishing recommendation.
          </p>
          <div className="mt-5 rounded-xl bg-slate-900/70 p-4 text-sm text-slate-300">
            {result?.recommendation
              ? formatValue(recommendation)
              : "Recommendation will appear after ORCA receives a query."}
          </div>
        </section>

        <section className="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-amber-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Risk Factors</h2>
          </div>
          <div className="mt-4 space-y-3 text-sm text-slate-400">
            {riskFactors.length > 0 ? (
              riskFactors.map((factor, index) => (
                <div key={`${factor}-${index}`} className="rounded-lg bg-slate-900/60 p-3">
                  {factor}
                </div>
              ))
            ) : result?.risk ? (
              <div className="whitespace-pre-wrap rounded-lg bg-slate-900/60 p-3">
                {formatValue(risk)}
              </div>
            ) : (
              <div className="rounded-lg bg-slate-900/60 p-3">No live risk assessment yet.</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
