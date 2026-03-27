import { client } from "./client";
import { Contact } from "./types";

export const contactsApi = {
  list: (params?: any) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return client.request<{ items: Contact[]; total: number; page: number; pages: number }>(`/contacts${qs}`);
  },

  get: (id: string) => client.request<Contact>(`/contacts/${id}`),

  create: (data: Partial<Contact>) =>
    client.request<Contact>("/contacts", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Contact>) =>
    client.request<Contact>(`/contacts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  delete: (id: string) => client.request(`/contacts/${id}`, { method: "DELETE" }),
};
