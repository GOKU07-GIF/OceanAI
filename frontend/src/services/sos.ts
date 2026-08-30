import axios from "axios";

import api from "./api";


// ============================================================
// SOS STATUS TYPE
// ============================================================

export type SOSStatus =
  | "ACTIVE"
  | "RESOLVED"
  | "CANCELLED";


// ============================================================
// SOS INTERFACE
// ============================================================

export interface SOSRequest {
  id: number;

  latitude: number;
  longitude: number;

  user_id: number;

  station_id: number | null;

  station_distance_km: number | null;

  status: SOSStatus;

  created_at: string;
}


// ============================================================
// CREATE SOS DATA
// ============================================================

export interface CreateSOSData {
  latitude: number;
  longitude: number;
}


// ============================================================
// EXTRACT BACKEND ERROR MESSAGE
// ============================================================

function getErrorMessage(error: unknown): string {

  // Check if the error is an Axios error
  if (axios.isAxiosError(error)) {

    const responseData = error.response?.data;

    console.log(
      "SOS Backend Error:",
      responseData
    );

    // FastAPI normal error format:
    // {
    //   "detail": "You already have an active SOS request."
    // }
    if (
      responseData &&
      typeof responseData === "object" &&
      "detail" in responseData
    ) {

      const detail = responseData.detail;

      if (typeof detail === "string") {
        return detail;
      }
    }


    // Alternative backend format:
    // {
    //   "message": "Some error"
    // }
    if (
      responseData &&
      typeof responseData === "object" &&
      "message" in responseData
    ) {

      const message = responseData.message;

      if (typeof message === "string") {
        return message;
      }
    }


    // Check normal Axios error message
    if (
      error.message &&
      typeof error.message === "string"
    ) {
      return error.message;
    }
  }


  // If the error is already a normal JavaScript Error
  if (error instanceof Error) {
    return error.message;
  }


  // Final fallback
  return "Unable to send SOS. Please try again.";
}


// ============================================================
// CREATE SOS
// ============================================================

export async function createSOS(
  data: CreateSOSData
): Promise<SOSRequest> {

  try {

    const response = await api.post<SOSRequest>(
      "/sos/",
      data
    );

    return response.data;

  } catch (error: unknown) {

    const message = getErrorMessage(error);

    throw new Error(message);
  }
}


// ============================================================
// GET ONE SOS
// ============================================================

export async function getSOS(
  sosId: number
): Promise<SOSRequest> {

  try {

    const response = await api.get<SOSRequest>(
      `/sos/${sosId}`
    );

    return response.data;

  } catch (error: unknown) {

    throw new Error(
      getErrorMessage(error)
    );
  }
}


// ============================================================
// GET ALL SOS REQUESTS
// ============================================================

export async function getAllSOS(): Promise<SOSRequest[]> {

  try {

    const response = await api.get<SOSRequest[]>(
      "/sos/"
    );

    return response.data;

  } catch (error: unknown) {

    throw new Error(
      getErrorMessage(error)
    );
  }
}


// ============================================================
// UPDATE SOS STATUS
// ============================================================

export async function updateSOSStatus(
  sosId: number,
  status: SOSStatus
): Promise<SOSRequest> {

  try {

    const response = await api.put<SOSRequest>(
      `/sos/${sosId}/status`,
      {
        status,
      }
    );

    return response.data;

  } catch (error: unknown) {

    throw new Error(
      getErrorMessage(error)
    );
  }
}


// ============================================================
// RESOLVE SOS
// ============================================================

export async function resolveSOS(
  sosId: number
): Promise<SOSRequest> {

  return updateSOSStatus(
    sosId,
    "RESOLVED"
  );
}


// ============================================================
// CANCEL SOS
// ============================================================

export async function cancelSOS(
  sosId: number
): Promise<SOSRequest> {

  return updateSOSStatus(
    sosId,
    "CANCELLED"
  );
}