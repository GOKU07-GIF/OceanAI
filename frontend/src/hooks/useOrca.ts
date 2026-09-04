import { useMutation } from "@tanstack/react-query";
import { askOrca } from "../services/orca";
import type { OrcaRequest } from "../types/orca";

export function useOrca() {
  return useMutation({
    mutationFn: (data: OrcaRequest) => askOrca(data),
  });
}
