import { client } from "./client";
import { DashboardStats } from "./types";

export const dashboardApi = {
  get: () => client.request<DashboardStats>("/dashboard"),
};
