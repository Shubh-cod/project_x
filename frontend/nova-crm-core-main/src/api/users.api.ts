import { client } from "./client";
import { User } from "./types";

export const usersApi = {
  list: () => client.request<User[]>("/users"),

  get: (id: string) => client.request<User>(`/users/${id}`),

  update: (id: string, data: { full_name?: string; role?: string; is_active?: boolean }) =>
    client.request<User>(`/users/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};
