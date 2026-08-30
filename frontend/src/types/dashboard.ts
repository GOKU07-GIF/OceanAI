export interface DashboardStats {
  total_records: number;
  total_users: number;

  average_temperature: number;
  average_ph: number;

  salinity: number;
  oxygen: number;
  water_quality: number;

  active_alerts: number;
  active_sensors: number;

  ai_risk: string;
}