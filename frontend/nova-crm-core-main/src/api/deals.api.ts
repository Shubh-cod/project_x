import { client } from "./client";
import { Deal } from "./types";

export const dealsApi = {
  list: (params?: any) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return client.request<{ items: Deal[]; total: number }>(`/deals${qs}`);
  },

  get: (id: string) => client.request<Deal>(`/deals/${id}`),

  create: (data: Partial<Deal>) =>
    client.request<Deal>("/deals", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Deal>) =>
    client.request<Deal>(`/deals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  getPipeline: () => client.request<{ stages: any[] }>("/deals/pipeline"),
};
