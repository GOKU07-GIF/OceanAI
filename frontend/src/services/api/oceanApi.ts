import api from "../api";

export async function getOceanData() {
  const response = await api.get("/ocean/");
  return response.data;
}