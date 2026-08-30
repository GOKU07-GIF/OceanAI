import OceanMap from "../../components/map/OceanMap";

export default function Map(): React.JSX.Element {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">
          Ocean Map
        </h1>

        <p className="mt-1 text-sm text-slate-400">
          Live ocean monitoring stations
        </p>
      </div>

      <OceanMap />
    </div>
  );
}