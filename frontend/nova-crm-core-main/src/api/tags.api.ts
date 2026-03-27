import { client } from "./client";
import { Tag } from "./types";

export const tagsApi = {
  list: () => client.request<Tag[]>("/tags"),

  get: (id: string) => client.request<Tag>(`/tags/${id}`),

  create: (data: { name: string }) =>
    client.request<Tag>("/tags", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: { name?: string }) =>
    client.request<Tag>(`/tags/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  delete: (id: string) => client.request(`/tags/${id}`, { method: "DELETE" }),
};
