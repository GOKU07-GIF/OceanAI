import api from "./api";

// ============================================================
// ALERT TYPES
// ============================================================

export type AlertType =
  | "SOS"
  | "WEATHER"
  | "SYSTEM"
  | "WARNING";

export type AlertSeverity =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";

// ============================================================
// ALERT INTERFACE
// ============================================================

export interface AlertResponse {
  id: number;

  title: string;
  message: string;

  alert_type: AlertType;
  severity: AlertSeverity;

  is_read: boolean;

  user_id: number | null;
  sos_id: number | null;

  created_at: string;
}

// ============================================================
// GET ALL ALERTS
// ============================================================

export async function getAllAlerts(): Promise<AlertResponse[]> {
  const response = await api.get<AlertResponse[]>(
    "/alerts/"
  );

  return response.data;
}