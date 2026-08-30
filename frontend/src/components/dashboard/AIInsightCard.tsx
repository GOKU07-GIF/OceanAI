interface AIInsightCardProps {
  seaHealthScore?: number;
  riskLevel?: string;
  message?: string;
}

export default function AIInsightCard({
  seaHealthScore = 97,
  riskLevel = "Low",
  message = "Marine ecosystem appears healthy.",
}: AIInsightCardProps): React.JSX.Element {
  const riskColor =
    riskLevel === "Low"
      ? "text-green-400"
      : riskLevel === "Medium"
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6 shadow-lg">
      <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-cyan-400">
        🤖 AI Insight
      </h2>

      <p className="text-slate-300">
        Sea Health Score:{" "}
        <span className="font-semibold text-white">
          {seaHealthScore}%
        </span>
      </p>

      <p className={`mt-2 font-semibold ${riskColor}`}>
        Risk Level: {riskLevel}
      </p>

      <p className="mt-4 text-slate-400">
        {message}
      </p>
    </div>
  );
}