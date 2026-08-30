import { useQuery } from "@tanstack/react-query";

import { getOceanData } from "../services/ocean";
import type { OceanData } from "../types/ocean";

export function useOceanData() {
  return useQuery<OceanData[]>({
    queryKey: ["ocean-data"],
    queryFn: getOceanData,
    refetchInterval: 10000,
  });
}