import { client } from "./client";
import { Deal } from "./types";

export const dealsApi = {
  list: (params?: Record<string, any>) => {
    const filtered = params
      ? Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
      : null;
    const qs = filtered && Object.keys(filtered).length
      ? "?" + new URLSearchParams(filtered as Record<string, string>).toString()
      : "";
    return client.request<{ items: Deal[]; total: number }>(`/deals${qs}`);
  },

  get: (id: string) => client.request<Deal>(`/deals/${id}`),

  create: (data: Partial<Deal>) =>
    client.request<Deal>("/deals", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Deal>) =>
    client.request<Deal>(`/deals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  getPipeline: () => client.request<{ stages: any[] }>("/deals/pipeline"),
};
