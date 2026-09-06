import { useEffect, useState } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface OrcaLocationPickerProps {
  latitude: number | null;
  longitude: number | null;
  onSelect: (latitude: number, longitude: number) => void;
}

function MapClickHandler({
  onSelect,
}: {
  onSelect: OrcaLocationPickerProps["onSelect"];
}): null {
  useMapEvents({
    click(event) {
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

function MapLocationSync({
  latitude,
  longitude,
}: {
  latitude: number | null;
  longitude: number | null;
}): null {
  const map = useMap();

  useEffect(() => {
    if (latitude === null || longitude === null) return;

    map.setView([latitude, longitude], Math.max(map.getZoom(), 7), {
      animate: true,
    });
  }, [latitude, longitude, map]);

  return null;
}

export default function OrcaLocationPicker({
  latitude,
  longitude,
  onSelect,
}: OrcaLocationPickerProps): React.JSX.Element {
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  const detectLocation = (): void => {
    setLocationError(null);

    if (!navigator.geolocation) {
      setLocationError("Location detection is not supported by this browser.");
      return;
    }

    setIsLocating(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextLatitude = position.coords.latitude;
        const nextLongitude = position.coords.longitude;

        onSelect(nextLatitude, nextLongitude);
        setIsLocating(false);
      },
      (error) => {
        let message = "Unable to detect your location.";

        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = "Location permission was denied. Allow it in your browser and try again.";
            break;
          case error.POSITION_UNAVAILABLE:
            message = "Your current location is unavailable. Try again in a moment.";
            break;
          case error.TIMEOUT:
            message = "Location detection timed out. Try again.";
            break;
          default:
            break;
        }

        setLocationError(message);
        setIsLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="button"
          onClick={detectLocation}
          disabled={isLocating}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2.5 text-sm font-semibold text-cyan-300 transition hover:border-cyan-400/50 hover:bg-cyan-500/15 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span aria-hidden="true">⌖</span>
          {isLocating ? "Detecting location..." : "Use my location"}
        </button>

        {locationError && (
          <p className="text-xs text-amber-300" role="alert">
            {locationError}
          </p>
        )}
      </div>

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
          <MapLocationSync latitude={latitude} longitude={longitude} />

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
    </div>
  );
}
