import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createSOS,
  getAllSOS,
  updateSOSStatus,
  type CreateSOSData,
  type SOSStatus,
} from "../services/sos";


// ============================================================
// GET ALL SOS REQUESTS
// ============================================================

export function useAllSOS() {
  return useQuery({
    queryKey: ["sos"],
    queryFn: getAllSOS,

    // Automatically refresh SOS data every 10 seconds
    refetchInterval: 10000,
  });
}


// ============================================================
// CREATE SOS
// ============================================================

export function useCreateSOS() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSOSData) =>
      createSOS(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sos"],
      });
    },
  });
}


// ============================================================
// UPDATE SOS STATUS
// ============================================================

export function useUpdateSOSStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sosId,
      status,
    }: {
      sosId: number;
      status: SOSStatus;
    }) =>
      updateSOSStatus(
        sosId,
        status
      ),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sos"],
      });
    },
  });
}