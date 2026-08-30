import { useMutation } from "@tanstack/react-query";
import { createSOS } from "../services/sos";

export function useCreateSOS() {
  return useMutation({
    mutationFn: createSOS,
  });
}