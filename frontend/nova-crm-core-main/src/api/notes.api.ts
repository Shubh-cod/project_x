import { client } from "./client";
import { Note, PaginatedResponse } from "./types";

export const notesApi = {
  listByEntity: (entityType: string, entityId: string, page = 1, pageSize = 20) =>
    client.request<PaginatedResponse<Note>>(
      `/notes?entity_type=${entityType}&entity_id=${entityId}&page=${page}&page_size=${pageSize}`
    ),

  get: (id: string) => client.request<Note>(`/notes/${id}`),

  create: (data: { entity_type: string; entity_id: string; content: string }) =>
    client.request<Note>("/notes", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: { content?: string }) =>
    client.request<Note>(`/notes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),

  delete: (id: string) => client.request(`/notes/${id}`, { method: "DELETE" }),
};
