import { client } from "./client";
import { Contact } from "./types";

export const contactsApi = {
  list: (params?: Record<string, any>) => {
    const filtered = params
      ? Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
      : null;
    const qs = filtered && Object.keys(filtered).length
      ? "?" + new URLSearchParams(filtered as Record<string, string>).toString()
      : "";
    return client.request<{ items: Contact[]; total: number; page: number; pages: number }>(`/contacts${qs}`);
  },

  get: (id: string) => client.request<Contact>(`/contacts/${id}`),

  create: (data: Partial<Contact>) =>
    client.request<Contact>("/contacts", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Contact>) =>
    client.request<Contact>(`/contacts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  delete: (id: string, deleteAssociated?: boolean) => {
    const qs = deleteAssociated ? "?delete_associated=true" : "";
    return client.request(`/contacts/${id}${qs}`, { method: "DELETE" });
  },
};
