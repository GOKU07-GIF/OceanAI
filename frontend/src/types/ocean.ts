export interface OceanData {
  id: number;
  latitude: number;
  longitude: number;
  temperature: number;
  ph: number;
  salinity: number;
  oxygen: number;
  is_active: boolean;
  owner_id: number;
  created_at: string;
}