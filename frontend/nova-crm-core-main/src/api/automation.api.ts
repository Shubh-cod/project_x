import { client } from "./client";
import { AutomationRule } from "./types";

export const automationApi = {
  listRules: (params?: Record<string, any>) => {
    const filtered = params
      ? Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
      : null;
    const qs = filtered && Object.keys(filtered).length
      ? "?" + new URLSearchParams(filtered as Record<string, string>).toString()
      : "";
    return client.request<{ items: AutomationRule[]; total: number }>(`/automation/rules${qs}`);
  },

  createRule: (data: Partial<AutomationRule>) =>
    client.request<AutomationRule>("/automation/rules", { method: "POST", body: JSON.stringify(data) }),

  updateRule: (id: string, data: Partial<AutomationRule>) =>
    client.request<AutomationRule>(`/automation/rules/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  deleteRule: (id: string) =>
    client.request(`/automation/rules/${id}`, { method: "DELETE" }),
};
