import api from "./api";
import type { OrcaRequest, OrcaResponse } from "../types/orca";

const ORCA_REQUEST_TIMEOUT_MS = 120_000;

export async function askOrca(data: OrcaRequest): Promise<OrcaResponse> {
  const response = await api.post<OrcaResponse>("/orca/plan", data, {
    timeout: ORCA_REQUEST_TIMEOUT_MS,
  });
  return response.data;
}
