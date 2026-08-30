import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  updateOceanData,
} from "../services/ocean";

import type { OceanData } from "../types/ocean";


export function useUpdateOceanData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ocean: OceanData) =>
      updateOceanData(ocean.id, ocean),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["ocean-data"],
      });
    },
  });
}