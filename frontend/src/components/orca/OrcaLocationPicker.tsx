import { useMapEvents, MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface OrcaLocationPickerProps {
  latitude: number | null;
  longitude: number | null;
  onSelect: (latitude: number, longitude: number) => void;
}

function MapClickHandler({ onSelect }: { onSelect: OrcaLocationPickerProps["onSelect"] }): null {
  useMapEvents({
    click(event) {
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

export default function OrcaLocationPicker({
  latitude,
  longitude,
  onSelect,
}: OrcaLocationPickerProps): React.JSX.Element {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-700">
      <MapContainer
        center={[15.5, 73.5]}
        zoom={5}
        scrollWheelZoom
        className="h-[320px] w-full"
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onSelect={onSelect} />

        {latitude !== null && longitude !== null && (
          <CircleMarker
            center={[latitude, longitude]}
            radius={10}
            pathOptions={{
              color: "#06b6d4",
              fillColor: "#06b6d4",
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <div className="text-sm">
                <strong>ORCA selected location</strong>
                <br />
                {latitude.toFixed(5)}, {longitude.toFixed(5)}
              </div>
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>
    </div>
  );
}
