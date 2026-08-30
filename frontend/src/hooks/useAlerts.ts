import { useQuery } from "@tanstack/react-query";

import {
  getAllAlerts,
  type AlertResponse,
} from "../services/alert";


export function useAllAlerts() {
  return useQuery<AlertResponse[]>({
    queryKey: ["alerts"],
    queryFn: getAllAlerts,
    refetchInterval: 10000,
  });
}