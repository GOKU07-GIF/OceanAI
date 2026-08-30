export default function MapPlaceholder(): React.JSX.Element {
  return (
    <div className="flex h-96 items-center justify-center rounded-2xl border border-dashed border-cyan-500 bg-slate-900 shadow-lg">
      <div className="text-center">
        <div className="mb-4 text-6xl">
          🌍
        </div>

        <h2 className="text-2xl font-bold text-cyan-400">
          Interactive Ocean Map
        </h2>

        <p className="mt-2 text-slate-400">
          Live ocean monitoring map will appear here.
        </p>
      </div>
    </div>
  );
}