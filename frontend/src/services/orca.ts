import api from "./api";
import type { OrcaRequest, OrcaResponse } from "../types/orca";

export async function askOrca(data: OrcaRequest): Promise<OrcaResponse> {
  const response = await api.post<OrcaResponse>("/orca/plan", data);
  return response.data;
}
