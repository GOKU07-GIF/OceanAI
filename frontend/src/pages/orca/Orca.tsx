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
import OrcaLocationPicker from "../../components/orca/OrcaLocationPicker";

interface ConditionCardProps {
  label: string;
  value: string;
  unit?: string;
  icon: React.ReactNode;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
}

function ConditionCard({ label, value, unit, icon }: ConditionCardProps): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold text-white">
            {value}
            {unit && value !== "Unavailable" && <span className="ml-1 text-sm font-normal text-slate-400">{unit}</span>}
          </p>
        </div>
        <div className="rounded-xl bg-slate-700 p-3 text-cyan-400">{icon}</div>
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (value == null) return "Unavailable";
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function getObjectValue(value: unknown, key: string): unknown {
  if (typeof value !== "object" || value === null) return undefined;
  return key in value ? (value as Record<string, unknown>)[key] : undefined;
}

function getStringValue(value: unknown, key: string): string | undefined {
  const item = getObjectValue(value, key);
  return typeof item === "string" ? item : undefined;
}

function collectStrings(value: unknown): string[] {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) return value.flatMap(collectStrings);
  if (typeof value === "object" && value !== null) return Object.values(value).flatMap(collectStrings);
  return [];
}

function collectEvidenceRecords(value: unknown): OrcaEvidence[] {
  if (Array.isArray(value)) return value.flatMap(collectEvidenceRecords);
  if (typeof value !== "object" || value === null) return [];

  const object = value as Record<string, unknown>;
  const records: OrcaEvidence[] = [];
  if (typeof object.metric === "string" || "value" in object) records.push(object as OrcaEvidence);

  for (const child of Object.values(object)) records.push(...collectEvidenceRecords(child));
  return records;
}

function findNestedValue(value: unknown, names: string[]): unknown {
  const wanted = names.map((name) => name.toLowerCase());
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findNestedValue(item, names);
      if (found !== undefined) return found;
    }
    return undefined;
  }
  if (typeof value !== "object" || value === null) return undefined;

  const object = value as Record<string, unknown>;
  for (const [key, item] of Object.entries(object)) {
    const normalized = key.toLowerCase().replaceAll("-", "_");
    if (wanted.some((name) => normalized === name || normalized.includes(name))) return item;
  }
  for (const item of Object.values(object)) {
    const found = findNestedValue(item, names);
    if (found !== undefined) return found;
  }
  return undefined;
}

function getEvidenceValue(response: OrcaResponse | undefined, names: string[]): string {
  if (!response) return "Unavailable";
  const records = collectEvidenceRecords(response.evidence);
  const recordMatch = records.find((item) => {
    const metric = item.metric?.toLowerCase();
    return metric ? names.some((name) => metric.includes(name)) : false;
  });
  if (recordMatch?.value != null) return formatValue(recordMatch.value);

  const nestedValue = findNestedValue(response.evidence, names);
  return nestedValue == null ? "Unavailable" : formatValue(nestedValue);
}

function getDecisionPresentation(decision?: string): {
  label: string;
  description: string;
  container: string;
  badge: string;
  icon: React.ReactNode;
} {
  const normalized = decision?.toUpperCase() ?? "";

  if (normalized === "SAFE" || normalized === "SUITABLE" || normalized === "GO") {
    return {
      label: "SAFE TO PROCEED",
      description: "Available evidence supports proceeding, subject to normal maritime precautions.",
      container: "border-green-500/30 bg-green-500/10",
      badge: "border-green-400/30 bg-green-400/10 text-green-300",
      icon: <CheckCircle2 size={28} className="text-green-400" />,
    };
  }

  if (normalized === "UNSAFE" || normalized === "NO_GO" || normalized === "DANGER") {
    return {
      label: "UNSAFE TO PROCEED",
      description: "Available evidence indicates conditions may be unsafe. Follow official maritime guidance.",
      container: "border-red-500/30 bg-red-500/10",
      badge: "border-red-400/30 bg-red-400/10 text-red-300",
      icon: <AlertTriangle size={28} className="text-red-400" />,
    };
  }

  if (normalized === "CAUTION" || normalized === "CONDITIONAL" || normalized === "WARNING") {
    return {
      label: "PROCEED WITH CAUTION",
      description: "Conditions require additional caution. Review the risk factors before deciding.",
      container: "border-amber-500/30 bg-amber-500/10",
      badge: "border-amber-400/30 bg-amber-400/10 text-amber-300",
      icon: <AlertTriangle size={28} className="text-amber-400" />,
    };
  }

  return {
    label: "INSUFFICIENT EVIDENCE",
    description: "A reliable go/no-go decision cannot be made until the required marine evidence is available.",
    container: "border-amber-500/30 bg-amber-500/10",
    badge: "border-amber-400/30 bg-amber-400/10 text-amber-300",
    icon: <AlertTriangle size={28} className="text-amber-400" />,
  };
}

export default function Orca(): React.JSX.Element {
  const [query, setQuery] = useState("");
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const orca = useOrca();
  const result = orca.data;

  const handleLocationSelect = (selectedLatitude: number, selectedLongitude: number): void => {
    setLatitude(selectedLatitude);
    setLongitude(selectedLongitude);
  };

  const handleAsk = (): void => {
    const trimmed = query.trim();
    if (!trimmed || orca.isPending) return;

    const userMessage: ChatMessage = { id: `${Date.now()}-user`, role: "user", text: trimmed };
    setMessages((current) => [...current, userMessage]);
    setQuery("");

    orca.mutate(
      {
        query: trimmed,
        language: "en",
        ...(latitude !== null && longitude !== null ? { latitude, longitude } : {}),
        ...(conversationId ? { conversation_id: conversationId } : {}),
      },
      {
        onSuccess: (response) => {
          if (response.conversation_id) setConversationId(response.conversation_id);
          const assistantText = response.assistant_response ?? getStringValue(response.recommendation, "recommendation") ?? "ORCA returned structured data without a response message.";
          setMessages((current) => [...current, { id: `${Date.now()}-assistant`, role: "assistant", text: assistantText }]);
        },
      },
    );
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>): void => {
    if (event.key === "Enter") handleAsk();
  };

  const startNewConversation = (): void => {
    setConversationId(undefined);
    setMessages([]);
    setQuery("");
    orca.reset();
  };

  const recommendation = result?.recommendation;
  const recommendationDecision = getStringValue(recommendation, "decision");
  const recommendationText = getStringValue(recommendation, "recommendation");
  const recommendationConfidence = getStringValue(recommendation, "confidence");
  const recommendationRisk = getStringValue(recommendation, "risk_level");
  const recommendationFactorList = collectStrings(getObjectValue(recommendation, "factors"));

  const riskAssessment = result?.risk_assessment;
  const riskLevel = getStringValue(riskAssessment, "level") ?? getStringValue(riskAssessment, "risk_level") ?? recommendationRisk;
  const riskFactors = collectStrings(getObjectValue(riskAssessment, "factors"));
  const effectiveRiskFactors = riskFactors.length > 0 ? riskFactors : recommendationFactorList;

  const responseText = result?.assistant_response;
  const hasStructuredRecommendation = Boolean(recommendationDecision || recommendationText || recommendationConfidence || recommendationRisk);
  const decisionPresentation = getDecisionPresentation(recommendationDecision);

  const seaTemperature = getEvidenceValue(result, ["sea_temperature", "sst_c", "temperature"]);
  const waveHeight = getEvidenceValue(result, ["wave_height", "wave_height_m"]);
  const windSpeed = getEvidenceValue(result, ["wind_speed", "wind_speed_m_s"]);
  const evidenceLocation = getEvidenceValue(result, ["location"]);
  const selectedLocation = latitude !== null && longitude !== null ? `${latitude.toFixed(4)}, ${longitude.toFixed(4)}` : evidenceLocation;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400"><Bot size={30} /></div>
          <div><h1 className="text-3xl font-bold text-white">ORCA Assistant</h1><p className="mt-1 text-sm text-slate-400">Ocean Research & Catch Advisory</p></div>
        </div>
        <div className="flex items-center gap-2 self-start rounded-full border border-green-500/20 bg-green-500/10 px-4 py-2 text-sm font-medium text-green-400 md:self-auto"><span className="h-2 w-2 rounded-full bg-green-400" /> Ready</div>
      </div>

      <section className="rounded-2xl border border-cyan-500/20 bg-slate-800 p-6 shadow-lg shadow-cyan-950/10">
        <div className="flex items-center justify-between gap-3"><div className="flex items-center gap-2 text-white"><MessageCircle size={20} className="text-cyan-400" /><h2 className="text-xl font-semibold">Ask ORCA</h2></div>{messages.length > 0 && <button type="button" onClick={startNewConversation} className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-400 transition hover:border-cyan-500/40 hover:text-cyan-300">New conversation</button>}</div>
        <p className="mt-2 text-sm text-slate-400">Ask about ocean conditions, fishing suitability, safety, or marine observations.</p>
        <div className="mt-5 flex flex-col gap-3 md:flex-row"><input type="text" value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={handleKeyDown} placeholder="e.g. Is it safe to go fishing near Mumbai tomorrow?" className="min-w-0 flex-1 rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-cyan-400" /><button type="button" onClick={handleAsk} disabled={!query.trim() || orca.isPending} className="flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50">{orca.isPending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}{orca.isPending ? "Thinking..." : "Ask ORCA"}</button></div>
        <div className="mt-4 flex flex-wrap gap-2">{["Fishing conditions near Mumbai", "Ocean safety tomorrow", "Best conditions for fishing"].map((question) => <button key={question} type="button" onClick={() => setQuery(question)} className="rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 transition hover:border-cyan-500/50 hover:text-cyan-300">{question}</button>)}</div>
      </section>

      {messages.length > 0 && <section className="rounded-2xl border border-slate-700 bg-slate-800 p-6"><div className="flex items-center gap-2 text-white"><MessageCircle size={20} className="text-cyan-400" /><h2 className="text-xl font-semibold">Conversation</h2>{conversationId && <span className="text-xs text-slate-600">Session active</span>}</div><div className="mt-4 max-h-96 space-y-4 overflow-y-auto pr-1">{messages.map((message) => <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === "user" ? "bg-cyan-500 text-slate-950" : "border border-slate-700 bg-slate-900 text-slate-200"}`}><p className="mb-1 text-[10px] font-semibold uppercase tracking-wider opacity-60">{message.role === "user" ? "You" : "ORCA"}</p><p className="whitespace-pre-wrap">{message.text}</p></div></div>)}{orca.isPending && <div className="flex justify-start"><div className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-400"><Loader2 size={16} className="mr-2 inline animate-spin" />ORCA is thinking...</div></div>}</div></section>}

      <section className="rounded-2xl border border-slate-700 bg-slate-800 p-6"><div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><div><div className="flex items-center gap-2 text-white"><MapPin size={20} className="text-cyan-400" /><h2 className="text-xl font-semibold">Select Ocean Location</h2></div><p className="mt-2 text-sm text-slate-400">Click anywhere on the map to send that latitude and longitude with your ORCA query.</p></div>{latitude !== null && longitude !== null && <div className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-3 py-2 text-xs text-cyan-300">Selected: {latitude.toFixed(4)}, {longitude.toFixed(4)}</div>}</div><div className="mt-4"><OrcaLocationPicker latitude={latitude} longitude={longitude} onSelect={handleLocationSelect} /></div></section>

      <section className="rounded-2xl border border-slate-700 bg-slate-800 p-6"><div className="flex items-center gap-3"><div className="rounded-xl bg-cyan-500/10 p-2 text-cyan-400"><Bot size={22} /></div><div><h2 className="font-semibold text-white">ORCA Recommendation</h2><p className="text-xs text-slate-500">{orca.isPending ? "Analyzing your request" : result ? "Latest ORCA response" : "Waiting for your question"}</p></div></div><div className="mt-5 rounded-xl border border-slate-700 bg-slate-900/60 p-6">
        {orca.isPending && <div className="flex flex-col items-center justify-center text-center"><Loader2 size={32} className="animate-spin text-cyan-400" /><p className="mt-3 text-slate-300">ORCA is analyzing ocean conditions...</p><p className="mt-1 text-xs text-slate-600">This may take a few moments.</p></div>}
        {orca.isError && !orca.isPending && <div className="text-center"><AlertTriangle size={32} className="mx-auto text-amber-400" /><p className="mt-3 text-slate-300">Unable to reach ORCA right now.</p><p className="mt-1 text-xs text-slate-500">{orca.error instanceof Error ? orca.error.message : "Please try again."}</p></div>}
        {!orca.isPending && !orca.isError && result && hasStructuredRecommendation && <div className="space-y-4">
          <div className={`rounded-2xl border p-5 ${decisionPresentation.container}`}>
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex items-center gap-3">{decisionPresentation.icon}<div><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">ORCA Safety Decision</p><h3 className="mt-1 text-2xl font-bold text-white">{decisionPresentation.label}</h3></div></div>
              <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${decisionPresentation.badge}`}>{recommendationDecision?.replaceAll("_", " ") ?? "INSUFFICIENT EVIDENCE"}</span>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-200">{recommendationText ?? decisionPresentation.description}</p>
            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2"><div className="rounded-xl bg-slate-950/30 p-4"><p className="text-xs uppercase tracking-wide text-slate-400">Confidence</p><p className="mt-1 text-lg font-semibold text-white">{recommendationConfidence ?? "Unavailable"}</p></div><div className="rounded-xl bg-slate-950/30 p-4"><p className="text-xs uppercase tracking-wide text-slate-400">Risk Level</p><p className="mt-1 text-lg font-semibold text-white">{riskLevel ?? "Unavailable"}</p></div></div>
          </div>
          {recommendationFactorList.length > 0 && <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Why ORCA reached this decision</p><ul className="mt-3 space-y-2 text-sm text-slate-300">{recommendationFactorList.map((factor, index) => <li key={`${factor}-${index}`} className="flex gap-2"><span className="text-cyan-400">•</span><span>{factor}</span></li>)}</ul></div>}
        </div>}
        {!orca.isPending && !orca.isError && result && !hasStructuredRecommendation && responseText && <div className="whitespace-pre-wrap text-sm leading-6 text-slate-200">{responseText}</div>}
        {!orca.isPending && !orca.isError && result && !hasStructuredRecommendation && !responseText && <div className="text-center"><Compass size={32} className="mx-auto text-slate-600" /><p className="mt-3 text-slate-400">ORCA returned data, but no displayable response text.</p></div>}
        {!orca.isPending && !orca.isError && !result && <div className="text-center"><Compass size={32} className="mx-auto text-slate-600" /><p className="mt-3 text-slate-400">Ask ORCA a question to generate an ocean intelligence recommendation.</p><p className="mt-1 text-xs text-slate-600">The backend response will appear here after you submit a query.</p></div>}
      </div></section>

      <section><div className="mb-4"><h2 className="text-xl font-semibold text-white">Environment Snapshot</h2><p className="mt-1 text-sm text-slate-400">Only verified environmental evidence returned by ORCA is shown here.</p></div><div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"><ConditionCard label="Sea Temperature" value={seaTemperature} unit="°C" icon={<Thermometer size={22} />} /><ConditionCard label="Wave Height" value={waveHeight} unit="m" icon={<Waves size={22} />} /><ConditionCard label="Wind Speed" value={windSpeed} unit="m/s" icon={<Wind size={22} />} /><ConditionCard label="Location" value={selectedLocation} icon={<MapPin size={22} />} /></div>{result?.evidence && <div className="mt-4 rounded-2xl border border-slate-700 bg-slate-800 p-5"><h3 className="font-semibold text-white">Evidence Returned by ORCA</h3><div className="mt-4 space-y-3">{collectEvidenceRecords(result.evidence).map((item, index) => <div key={`${item.metric ?? item.source ?? "evidence"}-${index}`} className="rounded-xl bg-slate-900/70 p-4"><div className="flex flex-wrap items-center gap-2 text-sm">{item.metric && <span className="font-medium text-cyan-300">{item.metric}</span>}{item.value != null && <span className="text-white">{formatValue(item.value)}</span>}{item.unit && <span className="text-slate-500">{item.unit}</span>}</div>{item.source && <p className="mt-1 text-xs text-slate-500">Source: {item.source}</p>}{item.timestamp && <p className="mt-1 text-xs text-slate-600">Time: {item.timestamp}</p>}</div>)}</div></div>}</section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2"><section className="rounded-2xl border border-green-500/20 bg-green-950/10 p-6"><div className="flex items-center gap-3"><CheckCircle2 className="text-green-400" size={24} /><h2 className="text-xl font-semibold text-white">Fishing Suitability</h2></div><p className="mt-4 text-slate-400">ORCA combines available environmental indicators to support the fishing recommendation.</p><div className="mt-5 rounded-xl bg-slate-900/70 p-4 text-sm text-slate-300">{recommendationText ?? "Recommendation will appear after ORCA receives a query."}</div></section><section className="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-6"><div className="flex items-center gap-3"><AlertTriangle className="text-amber-400" size={24} /><h2 className="text-xl font-semibold text-white">Risk Factors</h2></div><div className="mt-4 space-y-3 text-sm text-slate-400">{effectiveRiskFactors.length > 0 ? effectiveRiskFactors.map((factor, index) => <div key={`${factor}-${index}`} className="rounded-lg bg-slate-900/60 p-3">{factor}</div>) : riskLevel ? <div className="rounded-lg bg-slate-900/60 p-3">Risk level: <span className="font-semibold text-white">{riskLevel}</span></div> : <div className="rounded-lg bg-slate-900/60 p-3">No live risk assessment yet.</div>}</div></section></div>
    </div>
  );
}
