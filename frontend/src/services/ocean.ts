import api from "./api";
import type { OceanData } from "../types/ocean";


// GET ALL OCEAN DATA
export async function getOceanData(): Promise<OceanData[]> {
  const response = await api.get<OceanData[]>("/ocean/");
  return response.data;
}


// UPDATE OCEAN STATION
export async function updateOceanData(
  oceanId: number,
  ocean: OceanData
): Promise<OceanData> {
  const response = await api.put<OceanData>(
    `/ocean/${oceanId}`,
    {
      latitude: ocean.latitude,
      longitude: ocean.longitude,
      temperature: ocean.temperature,
      ph: ocean.ph,
      salinity: ocean.salinity,
      oxygen: ocean.oxygen,
      is_active: ocean.is_active,
    }
  );

  return response.data;
}