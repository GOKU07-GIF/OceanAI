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


// ============================================================
// USER LOCATION INTERFACE
// ============================================================

interface UserLocation {
  latitude: number;
  longitude: number;
}


// ============================================================
// OCEAN MAP COMPONENT
// ============================================================

export default function OceanMap(): React.JSX.Element {

  // ==========================================================
  // OCEAN DATA
  // ==========================================================

  const {
    data,
    isLoading,
    isError,
    error,
  } = useOceanData();


  // ==========================================================
  // SOS DATA
  // ==========================================================

  const {
    data: sosRequests = [],
    isLoading: isSOSLoading,
  } = useAllSOS();

  const createSOSMutation = useCreateSOS();

  const updateSOSStatusMutation =
    useUpdateSOSStatus();


  // ==========================================================
  // LOCATION STATE
  // ==========================================================

  const [userLocation, setUserLocation] =
    useState<UserLocation | null>(null);

  const [locationError, setLocationError] =
    useState<string | null>(null);


  // ==========================================================
  // SOS CONFIRMATION STATE
  // ==========================================================

  const [showSOSConfirm, setShowSOSConfirm] =
    useState(false);


  // ==========================================================
  // GET USER LOCATION
  // ==========================================================

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


  // ==========================================================
  // SEND SOS
  // ==========================================================

  function handleSendSOS() {

    if (!userLocation) {
      alert(
        "Your current location is not available yet."
      );

      return;
    }


    createSOSMutation.mutate(
      {
        latitude: userLocation.latitude,
        longitude: userLocation.longitude,
      },

      {
        onSuccess: () => {

          setShowSOSConfirm(false);

          alert(
            "Emergency SOS sent successfully!"
          );
        },

        onError: (error) => {

          alert(
            error instanceof Error
              ? error.message
              : "Failed to send SOS."
          );
        },
      }
    );
  }


  // ==========================================================
  // RESOLVE SOS
  // ==========================================================

  function handleResolveSOS(
    sosId: number
  ) {

    updateSOSStatusMutation.mutate(
      {
        sosId,
        status: "RESOLVED",
      },

      {
        onSuccess: () => {

          alert(
            "SOS has been resolved successfully."
          );
        },

        onError: (error) => {

          alert(
            error instanceof Error
              ? error.message
              : "Failed to resolve SOS."
          );
        },
      }
    );
  }


  // ==========================================================
  // CANCEL SOS
  // ==========================================================

  function handleCancelSOS(
    sosId: number
  ) {

    const confirmed = window.confirm(
      "Are you sure you want to cancel this SOS?"
    );


    if (!confirmed) {
      return;
    }


    updateSOSStatusMutation.mutate(
      {
        sosId,
        status: "CANCELLED",
      },

      {
        onSuccess: () => {

          alert(
            "SOS has been cancelled successfully."
          );
        },

        onError: (error) => {

          alert(
            error instanceof Error
              ? error.message
              : "Failed to cancel SOS."
          );
        },
      }
    );
  }


  // ==========================================================
  // LOADING OCEAN DATA
  // ==========================================================

  if (isLoading) {

    return (
      <div className="flex h-[500px] items-center justify-center rounded-2xl border border-slate-800 bg-slate-900">

        <p className="text-cyan-400">
          🌊 Loading ocean stations...
        </p>

      </div>
    );
  }


  // ==========================================================
  // OCEAN API ERROR
  // ==========================================================

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


  // ==========================================================
  // OCEAN DATA
  // ==========================================================

  const oceanData: OceanData[] = data ?? [];


  // ==========================================================
  // DEFAULT MAP CENTER
  // ==========================================================

  const mapCenter: [number, number] =
    oceanData.length > 0
      ? [
          oceanData[0].latitude,
          oceanData[0].longitude,
        ]
      : userLocation
        ? [
            userLocation.latitude,
            userLocation.longitude,
          ]
        : [
            19.0760,
            72.8777,
          ];


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="w-full space-y-6">


      {/* ====================================================== */}
      {/* MAP */}
      {/* ====================================================== */}

      <MapContainer
        center={mapCenter}
        zoom={6}
        scrollWheelZoom={true}
        className="h-[500px] w-full rounded-2xl"
      >


        {/* MAP TILES */}

        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />


        {/* ==================================================== */}
        {/* OCEAN STATIONS */}
        {/* ==================================================== */}

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


                {/* STATION HEADER */}

                <div className="border-b pb-2">

                  <h2 className="text-lg font-bold text-cyan-600">
                    🌊 OceanAI Station
                  </h2>

                  <p className="text-xs text-gray-500">
                    Station ID: {ocean.id}
                  </p>

                </div>


                {/* OCEAN DATA */}

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


                {/* STATUS */}

                <div className="rounded-lg bg-green-100 px-3 py-2 text-sm text-green-700">

                  🟢 Station Active

                </div>

              </div>

            </Popup>

          </Marker>

        ))}


        {/* ==================================================== */}
        {/* USER CURRENT LOCATION */}
        {/* ==================================================== */}

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

              <div className="w-56 space-y-2">

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


      {/* ====================================================== */}
      {/* LOCATION STATUS */}
      {/* ====================================================== */}

      {userLocation && (

        <p className="text-sm text-green-400">

          📍 Your current location is detected.

        </p>

      )}


      {locationError && (

        <p className="text-sm text-yellow-400">

          ⚠️ {locationError}

        </p>

      )}


      {/* ====================================================== */}
      {/* EMERGENCY SOS */}
      {/* ====================================================== */}

      <div className="rounded-2xl border border-red-500/40 bg-red-950/20 p-5">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">


          <div>

            <h2 className="text-xl font-bold text-red-300">

              🚨 Emergency SOS

            </h2>


            <p className="mt-1 text-sm text-slate-400">

              Send your current location to the OceanAI emergency system.

            </p>

          </div>


          <button
            type="button"
            onClick={() => setShowSOSConfirm(true)}
            disabled={
              !userLocation ||
              createSOSMutation.isPending
            }
            className="rounded-xl bg-red-600 px-6 py-3 font-bold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {createSOSMutation.isPending
              ? "Sending..."
              : "🚨 SEND SOS"}

          </button>

        </div>


        {/* ==================================================== */}
        {/* SOS CONFIRMATION */}
        {/* ==================================================== */}

        {showSOSConfirm && (

          <div className="mt-5 rounded-xl border border-red-500/40 bg-red-950/50 p-4">


            <h3 className="text-lg font-bold text-red-300">

              ⚠️ Confirm Emergency SOS

            </h3>


            <p className="mt-2 text-sm text-slate-300">

              Are you sure you want to send an emergency SOS?

            </p>


            <p className="mt-2 text-sm text-slate-400">

              Your current GPS location will be sent to the OceanAI emergency system.

            </p>


            <div className="mt-4 flex gap-3">


              <button
                type="button"
                onClick={() =>
                  setShowSOSConfirm(false)
                }
                className="rounded-lg bg-slate-600 px-4 py-2 font-semibold text-white transition hover:bg-slate-500"
              >

                Cancel

              </button>


              <button
                type="button"
                onClick={handleSendSOS}
                disabled={createSOSMutation.isPending}
                className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
              >

                {createSOSMutation.isPending
                  ? "Sending..."
                  : "🚨 Yes, Send SOS"}

              </button>

            </div>

          </div>

        )}

      </div>


      {/* ====================================================== */}
      {/* MY SOS REQUESTS */}
      {/* ====================================================== */}

      <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">


        <div className="mb-5">

          <h2 className="text-xl font-bold text-cyan-300">

            🚨 My SOS Requests

          </h2>


          <p className="mt-1 text-sm text-slate-400">

            View your emergency requests and their current status.

          </p>

        </div>


        {/* LOADING SOS */}

        {isSOSLoading && (

          <p className="text-slate-400">

            Loading SOS requests...

          </p>

        )}


        {/* NO SOS */}

        {!isSOSLoading &&
          sosRequests.length === 0 && (

            <p className="text-slate-500">

              No SOS requests found.

            </p>

          )}


        {/* SOS LIST */}

        <div className="space-y-4">

          {sosRequests.map((sos) => (

            <div
              key={sos.id}
              className="rounded-xl border border-slate-700 bg-slate-800 p-5"
            >


              {/* HEADER */}

              <div className="flex flex-wrap items-center justify-between gap-3">


                <h3 className="text-lg font-bold text-white">

                  🚨 SOS #{sos.id}

                </h3>


                <span
                  className={`rounded-full px-3 py-1 text-xs font-bold ${
                    sos.status === "ACTIVE"
                      ? "bg-green-500/20 text-green-400"
                      : sos.status === "RESOLVED"
                        ? "bg-blue-500/20 text-blue-400"
                        : "bg-yellow-500/20 text-yellow-400"
                  }`}
                >

                  {sos.status}

                </span>

              </div>


              {/* LOCATION */}

              <p className="mt-3 text-sm text-slate-400">

                📍 {sos.latitude.toFixed(6)},{" "}
                {sos.longitude.toFixed(6)}

              </p>


              {/* DETAILS */}

              <div className="mt-4 grid gap-3 text-sm text-slate-300 md:grid-cols-2 lg:grid-cols-4">


                <p>

                  🛰️ Station:{" "}

                  <span className="font-semibold">

                    {sos.station_id
                      ? `Station ${sos.station_id}`
                      : "Not assigned"}

                  </span>

                </p>


                <p>

                  📏 Distance:{" "}

                  <span className="font-semibold">

                    {sos.station_distance_km !== null
                      ? `${sos.station_distance_km.toFixed(2)} km`
                      : "N/A"}

                  </span>

                </p>


                <p>

                  👤 User ID:{" "}

                  <span className="font-semibold">

                    {sos.user_id}

                  </span>

                </p>


                <p>

                  🕒{" "}

                  {new Date(
                    sos.created_at
                  ).toLocaleString()}

                </p>

              </div>


              {/* ================================================= */}
              {/* RESOLVE AND CANCEL BUTTONS */}
              {/* ================================================= */}

              {sos.status === "ACTIVE" && (

                <div className="mt-5 flex flex-wrap gap-3">


                  {/* RESOLVE SOS */}

                  <button
                    type="button"
                    onClick={() =>
                      handleResolveSOS(sos.id)
                    }
                    disabled={
                      updateSOSStatusMutation.isPending
                    }
                    className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >

                    ✓ Resolve SOS

                  </button>


                  {/* CANCEL SOS */}

                  <button
                    type="button"
                    onClick={() =>
                      handleCancelSOS(sos.id)
                    }
                    disabled={
                      updateSOSStatusMutation.isPending
                    }
                    className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >

                    ✕ Cancel SOS

                  </button>

                </div>

              )}

            </div>

          ))}

        </div>

      </div>

    </div>

  );
}