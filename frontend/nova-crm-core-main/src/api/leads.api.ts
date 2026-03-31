import { client } from "./client";
import { Lead } from "./types";

export const leadsApi = {
  list: (params?: Record<string, any>) => {
    const filtered = params
      ? Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
      : null;
    const qs = filtered && Object.keys(filtered).length
      ? "?" + new URLSearchParams(filtered as Record<string, string>).toString()
      : "";
    return client.request<{ items: Lead[]; total: number; page: number; pages: number }>(`/leads${qs}`);
  },

  get: (id: string) => client.request<Lead>(`/leads/${id}`),

  create: (data: Partial<Lead>) =>
    client.request<Lead>("/leads", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Lead>) =>
    client.request<Lead>(`/leads/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  convert: (id: string, data: { create_deal: boolean; deal_title?: string; deal_value?: number }) =>
    client.request<{ contact: any; deal?: any }>(`/leads/${id}/convert`, { method: "POST", body: JSON.stringify(data) }),
};
