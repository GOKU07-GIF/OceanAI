import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  CircleMarker,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import { useOceanData } from "../../hooks/useOceanData";

import {
  useAllSOS,
  useCreateSOS,
  useUpdateSOSStatus,
} from "../../hooks/useSOS";

import type { OceanData } from "../../types/ocean";

interface UserLocation {
  latitude: number;
  longitude: number;
}

export default function OceanMap(): React.JSX.Element {
  // ============================================================
  // OCEAN DATA
  // ============================================================

  const {
    data,
    isLoading,
    isError,
    error,
  } = useOceanData();

  const oceanData: OceanData[] = data ?? [];


  // ============================================================
  // USER LOCATION
  // ============================================================

  const [userLocation, setUserLocation] =
    useState<UserLocation | null>(null);

  const [locationError, setLocationError] =
    useState<string | null>(null);


  // ============================================================
  // SOS STATE
  // ============================================================

  const [showSOSConfirmation, setShowSOSConfirmation] =
    useState(false);


  // ============================================================
  // SOS HISTORY
  // ============================================================

  const {
    data: sosRequests = [],
    isLoading: isLoadingSOS,
    isError: isSOSError,
  } = useAllSOS();


  // ============================================================
  // CREATE SOS
  // ============================================================

  const {
    mutate: createSOSRequest,
    isPending: isCreatingSOS,
    isError: isCreateSOSError,
    error: createSOSError,
  } = useCreateSOS();


  // ============================================================
  // UPDATE SOS STATUS
  // ============================================================

  const {
    mutate: updateSOSStatus,
    isPending: isUpdatingSOS,
  } = useUpdateSOSStatus();


  // ============================================================
  // GET CURRENT USER LOCATION
  // ============================================================

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationError(
        "Geolocation is not supported by this browser."
      );

      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });

        setLocationError(null);
      },

      () => {
        setLocationError(
          "Location permission was denied."
        );
      },

      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  }, []);


  // ============================================================
  // SEND SOS
  // ============================================================

  const handleSendSOS = () => {
  if (!userLocation) {
    setLocationError(
      "Your current location is required to send SOS."
    );

    return;
  }

  createSOSRequest(
    {
      latitude: userLocation.latitude,
      longitude: userLocation.longitude,
    },
    {
      onSuccess: () => {
        setShowSOSConfirmation(false);
      },
    }
  );
};

  // ============================================================
  // CANCEL SOS
  // ============================================================

  const handleCancelSOS = (sosId: number) => {
    updateSOSStatus({
      sosId,
      status: "CANCELLED",
    });
  };


  // ============================================================
  // RESOLVE SOS
  // ============================================================

  const handleResolveSOS = (sosId: number) => {
    updateSOSStatus({
      sosId,
      status: "RESOLVED",
    });
  };


  // ============================================================
  // LOADING OCEAN DATA
  // ============================================================

  if (isLoading) {
    return (
      <div className="flex h-[500px] items-center justify-center rounded-2xl border border-slate-800 bg-slate-900">
        <p className="text-cyan-400">
          🌊 Loading ocean stations...
        </p>
      </div>
    );
  }


  // ============================================================
  // OCEAN API ERROR
  // ============================================================

  if (isError) {
    return (
      <div className="flex h-[500px] items-center justify-center rounded-2xl border border-red-500/30 bg-slate-900">
        <div className="text-center">
          <p className="text-lg font-semibold text-red-400">
            Failed to load ocean stations
          </p>

          <p className="mt-2 text-sm text-slate-400">
            {(error as Error)?.message ||
              "Unable to connect to the ocean API."}
          </p>
        </div>
      </div>
    );
  }


  const firstLocation = oceanData[0];


  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div className="w-full space-y-6">

      {/* ====================================================== */}
      {/* OCEAN MAP */}
      {/* ====================================================== */}

      <div>
        <MapContainer
          center={
            firstLocation
              ? [
                  firstLocation.latitude,
                  firstLocation.longitude,
                ]
              : userLocation
                ? [
                    userLocation.latitude,
                    userLocation.longitude,
                  ]
                : [19.076, 72.8777]
          }
          zoom={6}
          scrollWheelZoom={true}
          className="h-[500px] w-full rounded-2xl"
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          {/* ================================================== */}
          {/* OCEAN STATIONS */}
          {/* ================================================== */}

          {oceanData.map((ocean) => (
            <Marker
              key={ocean.id}
              position={[
                ocean.latitude,
                ocean.longitude,
              ]}
            >
              <Popup>
                <div className="w-56 space-y-3">

                  <div className="border-b pb-2">
                    <h2 className="text-lg font-bold text-cyan-600">
                      🌊 OceanAI Station
                    </h2>

                    <p className="text-xs text-gray-500">
                      Station ID: {ocean.id}
                    </p>
                  </div>

                  <div className="space-y-2 text-sm">

                    <p>
                      🌡️ <strong>Temperature:</strong>{" "}
                      {ocean.temperature}°C
                    </p>

                    <p>
                      🧪 <strong>pH:</strong>{" "}
                      {ocean.ph}
                    </p>

                    <p>
                      🧂 <strong>Salinity:</strong>{" "}
                      {ocean.salinity} PSU
                    </p>

                    <p>
                      💨 <strong>Oxygen:</strong>{" "}
                      {ocean.oxygen} mg/L
                    </p>

                  </div>

                  <div className="rounded-lg bg-green-100 px-3 py-2 text-sm text-green-700">
                    🟢 Station Active
                  </div>

                </div>
              </Popup>
            </Marker>
          ))}


          {/* ================================================== */}
          {/* USER CURRENT LOCATION */}
          {/* ================================================== */}

          {userLocation && (
            <CircleMarker
              center={[
                userLocation.latitude,
                userLocation.longitude,
              ]}
              radius={10}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#3b82f6",
                fillOpacity: 0.8,
              }}
            >
              <Popup>
                <div className="w-56 space-y-3">

                  <h2 className="font-bold text-blue-600">
                    📍 Your Current Location
                  </h2>

                  <p>
                    Latitude:{" "}
                    {userLocation.latitude.toFixed(6)}
                  </p>

                  <p>
                    Longitude:{" "}
                    {userLocation.longitude.toFixed(6)}
                  </p>

                </div>
              </Popup>
            </CircleMarker>
          )}

        </MapContainer>


        {userLocation && (
          <p className="mt-3 text-sm text-green-400">
            📍 Your current location is detected.
          </p>
        )}

        {locationError && (
          <p className="mt-3 text-sm text-yellow-400">
            ⚠️ {locationError}
          </p>
        )}

      </div>


      {/* ====================================================== */}
      {/* EMERGENCY SOS */}
      {/* ====================================================== */}

      <div className="rounded-2xl border border-red-500/30 bg-red-950/20 p-5">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

          <div>
            <h2 className="text-xl font-bold text-red-300">
              🚨 Emergency SOS
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Send your current location to the OceanAI emergency system.
            </p>
          </div>

          <button
            onClick={() =>
              setShowSOSConfirmation(true)
            }
            disabled={!userLocation}
            className="rounded-xl bg-red-600 px-6 py-3 font-bold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            🚨 SEND SOS
          </button>

        </div>


        {/* SOS CONFIRMATION */}

        {showSOSConfirmation && (
          <div className="mt-5 rounded-xl border border-red-500/30 bg-red-950/50 p-4">

            <h3 className="text-lg font-bold text-red-300">
              ⚠️ Confirm Emergency SOS
            </h3>

            <p className="mt-2 text-sm text-slate-300">
              Are you sure you want to send an emergency SOS?
            </p>

            <p className="mt-2 text-xs text-slate-400">
              Your current GPS location will be sent to the OceanAI emergency system.
            </p>

            <div className="mt-4 flex gap-3">

              <button
                onClick={() =>
                  setShowSOSConfirmation(false)
                }
                disabled={isCreatingSOS}
                className="rounded-lg bg-slate-600 px-4 py-2 font-semibold text-white hover:bg-slate-500"
              >
                Cancel
              </button>

              <button
                onClick={handleSendSOS}
                disabled={isCreatingSOS}
                className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isCreatingSOS
                  ? "Sending..."
                  : "🚨 Yes, Send SOS"}
              </button>

            </div>

          </div>
        )}

        {/* SOS CREATE ERROR */}

        {isCreateSOSError && (
          <div className="mt-5 rounded-xl border border-red-500/40 bg-red-950/40 p-4">

            <h3 className="font-bold text-red-400">
              🚨 SOS could not be sent
            </h3>

            <p className="mt-2 text-sm text-slate-300">
              {createSOSError instanceof Error
                ? createSOSError.message
                : "Unable to send SOS. Please try again."}
            </p>

          </div>
        )}

      </div>


      {/* ====================================================== */}
      {/* MY SOS REQUESTS */}
      {/* ====================================================== */}

      <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">

        <h2 className="text-xl font-bold text-cyan-300">
          🚨 My SOS Requests
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          View your emergency requests and their current status.
        </p>


        {isLoadingSOS && (
          <p className="mt-5 text-cyan-400">
            Loading SOS requests...
          </p>
        )}


        {isSOSError && (
          <p className="mt-5 text-red-400">
            Failed to load SOS requests.
          </p>
        )}


        {!isLoadingSOS &&
          !isSOSError &&
          sosRequests.length === 0 && (
            <p className="mt-5 text-slate-500">
              No SOS requests found.
            </p>
          )}


        <div className="mt-5 space-y-4">

          {sosRequests.map((sos) => (
            <div
              key={sos.id}
              className="rounded-xl border border-slate-700 bg-slate-800/70 p-5"
            >

              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                <div>

                  <h3 className="text-lg font-bold text-white">
                    🚨 SOS #{sos.id}
                  </h3>

                  <p className="mt-2 text-sm text-slate-400">
                    📍 {Number(sos.latitude).toFixed(6)},{" "}
                    {Number(sos.longitude).toFixed(6)}
                  </p>

                </div>


                {/* STATUS */}

                <div
                  className={`rounded-full px-4 py-2 text-sm font-bold ${
                    sos.status === "ACTIVE"
                      ? "bg-green-500/20 text-green-400"
                      : sos.status === "CANCELLED"
                        ? "bg-yellow-500/20 text-yellow-400"
                        : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {sos.status}
                </div>

              </div>


              <div className="mt-5 flex flex-wrap gap-3">

                {/* CANCEL BUTTON */}

                {sos.status === "ACTIVE" && (
                  <button
                    onClick={() =>
                      handleCancelSOS(sos.id)
                    }
                    disabled={isUpdatingSOS}
                    className="rounded-lg bg-yellow-600 px-4 py-2 font-semibold text-white hover:bg-yellow-700 disabled:opacity-50"
                  >
                    {isUpdatingSOS
                      ? "Updating..."
                      : "✖ Cancel SOS"}
                  </button>
                )}


                {/* RESOLVE BUTTON */}

                {sos.status === "ACTIVE" && (
                  <button
                    onClick={() =>
                      handleResolveSOS(sos.id)
                    }
                    disabled={isUpdatingSOS}
                    className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isUpdatingSOS
                      ? "Updating..."
                      : "✓ Resolve SOS"}
                  </button>
                )}

              </div>

            </div>
          ))}

        </div>

      </div>

    </div>
  );
}