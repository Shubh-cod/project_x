import { client } from "./client";
import { Note } from "./types";

export const notesApi = {
  listByEntity: (type: string, id: string) =>
    client.request<Note[]>(`/notes/entity/${type}/${id}`),

  create: (data: { entity_type: string; entity_id: string; content: string }) =>
    client.request<Note>("/notes", { method: "POST", body: JSON.stringify(data) }),
};
