import {
  Bell,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
} from "lucide-react";

import {
  useAllAlerts,
} from "../../hooks/useAlerts";

import type {
  AlertResponse,
  AlertSeverity,
} from "../../services/alert";


// ============================================================
// ALERT SEVERITY STYLES
// ============================================================

const severityStyles: Record<
  AlertSeverity,
  {
    icon: typeof AlertTriangle;
    title: string;
    border: string;
    bg: string;
    badge: string;
  }
> = {
  CRITICAL: {
    icon: XCircle,
    title: "text-red-400",
    border: "border-red-500/40",
    bg: "bg-red-500/5",
    badge:
      "bg-red-500/20 text-red-400 border-red-500/30",
  },

  HIGH: {
    icon: AlertTriangle,
    title: "text-orange-400",
    border: "border-orange-500/40",
    bg: "bg-orange-500/5",
    badge:
      "bg-orange-500/20 text-orange-400 border-orange-500/30",
  },

  MEDIUM: {
    icon: AlertTriangle,
    title: "text-yellow-400",
    border: "border-yellow-500/40",
    bg: "bg-yellow-500/5",
    badge:
      "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  },

  LOW: {
    icon: Info,
    title: "text-cyan-400",
    border: "border-cyan-500/40",
    bg: "bg-cyan-500/5",
    badge:
      "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  },
};


// ============================================================
// FORMAT DATE
// ============================================================

function formatAlertTime(
  dateString: string
): string {

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return dateString;
  }

  const now = new Date();

  const difference =
    now.getTime() - date.getTime();

  const seconds = Math.floor(
    difference / 1000
  );

  const minutes = Math.floor(
    seconds / 60
  );

  const hours = Math.floor(
    minutes / 60
  );

  const days = Math.floor(
    hours / 24
  );


  if (seconds < 60) {
    return "Just now";
  }


  if (minutes < 60) {
    return `${minutes} minute${
      minutes !== 1 ? "s" : ""
    } ago`;
  }


  if (hours < 24) {
    return `${hours} hour${
      hours !== 1 ? "s" : ""
    } ago`;
  }


  if (days < 7) {
    return `${days} day${
      days !== 1 ? "s" : ""
    } ago`;
  }


  return date.toLocaleString();
}


// ============================================================
// ALERT PAGE
// ============================================================

export default function Alerts(): React.JSX.Element {

  // ==========================================================
  // FETCH ALERTS
  // ==========================================================

  const {
    data: alerts = [],
    isLoading,
    isError,
    error,
  } = useAllAlerts();


  // ==========================================================
  // SUMMARY COUNTS
  // ==========================================================

  const criticalAlerts =
    alerts.filter(
      (alert: AlertResponse) =>
        alert.severity === "CRITICAL"
    ).length;


  const warnings =
    alerts.filter(
      (alert: AlertResponse) =>
        alert.severity === "HIGH" ||
        alert.severity === "MEDIUM"
    ).length;


  // SYSTEM + WARNING type alerts
  // because AlertType currently supports:
  // SOS, WEATHER, SYSTEM, WARNING

  const systemUpdates =
    alerts.filter(
      (alert: AlertResponse) =>
        alert.alert_type === "SYSTEM"
    ).length;


  const unreadAlerts =
    alerts.filter(
      (alert: AlertResponse) =>
        !alert.is_read
    ).length;


  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <div className="space-y-6">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex items-center justify-between">

        <div>

          <h1 className="text-3xl font-bold text-white">
            Alerts
          </h1>

          <p className="mt-1 text-slate-400">
            Monitor important ocean events and system
            notifications.
          </p>

        </div>


        {/* Alert Counter */}

        <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2">

          <Bell
            size={20}
            className="text-cyan-400"
          />

          <span className="text-sm text-slate-300">
            {alerts.length} Alerts
          </span>


          {unreadAlerts > 0 && (

            <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs font-bold text-white">
              {unreadAlerts}
            </span>

          )}

        </div>

      </div>


      {/* ======================================================
          SUMMARY
      ====================================================== */}

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">


        {/* Critical */}

        <div className="rounded-2xl border border-red-500/30 bg-slate-800 p-5">

          <p className="text-sm text-slate-400">
            Critical Alerts
          </p>

          <p className="mt-2 text-3xl font-bold text-red-400">
            {criticalAlerts}
          </p>

        </div>


        {/* Warnings */}

        <div className="rounded-2xl border border-orange-500/30 bg-slate-800 p-5">

          <p className="text-sm text-slate-400">
            Warnings
          </p>

          <p className="mt-2 text-3xl font-bold text-orange-400">
            {warnings}
          </p>

        </div>


        {/* System Updates */}

        <div className="rounded-2xl border border-cyan-500/30 bg-slate-800 p-5">

          <p className="text-sm text-slate-400">
            System Updates
          </p>

          <p className="mt-2 text-3xl font-bold text-cyan-400">
            {systemUpdates}
          </p>

        </div>

      </div>


      {/* ======================================================
          ALERT LIST
      ====================================================== */}

      <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">


        {/* Header */}

        <div className="mb-5 flex items-center justify-between">

          <h2 className="text-xl font-semibold text-white">
            Recent Alerts
          </h2>

          <span className="text-sm text-slate-500">
            Auto-refreshes every 10 seconds
          </span>

        </div>


        {/* ====================================================
            LOADING
        ==================================================== */}

        {isLoading && (

          <div className="py-10 text-center">

            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-cyan-400 border-t-transparent" />

            <p className="mt-3 text-sm text-slate-400">
              Loading alerts...
            </p>

          </div>

        )}


        {/* ====================================================
            ERROR
        ==================================================== */}

        {isError && (

          <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5">

            <p className="font-semibold text-red-400">
              Unable to load alerts
            </p>

            <p className="mt-1 text-sm text-slate-400">
              {error instanceof Error
                ? error.message
                : "Please try again later."}
            </p>

          </div>

        )}


        {/* ====================================================
            EMPTY
        ==================================================== */}

        {!isLoading &&
          !isError &&
          alerts.length === 0 && (

            <div className="py-10 text-center">

              <CheckCircle
                size={42}
                className="mx-auto text-green-400"
              />

              <h3 className="mt-3 font-semibold text-white">
                No alerts found
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Everything looks good right now.
              </p>

            </div>

          )}


        {/* ====================================================
            ALERTS
        ==================================================== */}

        {!isLoading &&
          !isError &&
          alerts.length > 0 && (

            <div className="space-y-4">

              {alerts.map(
                (alert: AlertResponse) => {

                  const style =
                    severityStyles[
                      alert.severity
                    ];

                  const Icon =
                    style.icon;


                  return (

                    <div
                      key={alert.id}
                      className={`flex flex-col gap-4 rounded-xl border p-5 transition sm:flex-row sm:items-start ${
                        style.border
                      } ${
                        style.bg
                      } ${
                        !alert.is_read
                          ? "ring-1 ring-white/10"
                          : "opacity-75"
                      }`}
                    >


                      {/* ==================================================
                          ICON
                      ================================================== */}

                      <Icon
                        size={24}
                        className={`shrink-0 ${style.title}`}
                      />


                      {/* ==================================================
                          CONTENT
                      ================================================== */}

                      <div className="flex-1">


                        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">

                          <div>


                            {/* Title + Severity */}

                            <div className="flex flex-wrap items-center gap-2">

                              <h3
                                className={`font-semibold ${style.title}`}
                              >
                                {alert.title}
                              </h3>


                              {/* Severity */}

                              <span
                                className={`rounded-full border px-2 py-1 text-xs font-bold ${style.badge}`}
                              >
                                {alert.severity}
                              </span>


                              {/* Unread */}

                              {!alert.is_read && (

                                <span className="rounded-full bg-cyan-500/20 px-2 py-1 text-xs font-semibold text-cyan-300">
                                  NEW
                                </span>

                              )}

                            </div>


                            {/* Alert Type */}

                            <p className="mt-1 text-xs uppercase tracking-wider text-slate-500">

                              {alert.alert_type}

                              {alert.sos_id !== null && (
                                <>
                                  {" • "}
                                  SOS #{alert.sos_id}
                                </>
                              )}

                            </p>

                          </div>


                          {/* Time */}

                          <span className="shrink-0 text-sm text-slate-500">

                            {formatAlertTime(
                              alert.created_at
                            )}

                          </span>

                        </div>


                        {/* ==================================================
                            MESSAGE
                        ================================================== */}

                        <p className="mt-3 text-sm leading-6 text-slate-300">
                          {alert.message}
                        </p>


                      </div>

                    </div>

                  );

                }
              )}

            </div>

          )}

      </div>

    </div>
  );
}