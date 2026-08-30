import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateSOSStatus } from "../services/sos";


type SOSStatus =
  | "ACTIVE"
  | "RESOLVED"
  | "CANCELLED";


export function useUpdateSOSStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sosId,
      status,
    }: {
      sosId: number;
      status: SOSStatus;
    }) => {
      return updateSOSStatus(
        sosId,
        status
      );
    },

    onSuccess: () => {
      // Refresh SOS data after updating the status
      queryClient.invalidateQueries({
        queryKey: ["sos"],
      });
    },
  });
}