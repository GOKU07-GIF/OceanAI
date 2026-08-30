import { useQuery } from "@tanstack/react-query";
import { getDashboardStats } from "../services/dashboard";
import { DashboardStats } from "../types/dashboard";

export function useDashboard() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard"],
    queryFn: getDashboardStats,
    refetchInterval: 10000,
  });
}