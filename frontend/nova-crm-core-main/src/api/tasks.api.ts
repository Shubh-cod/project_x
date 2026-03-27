import { client } from "./client";
import { Task } from "./types";

export const tasksApi = {
  list: (params?: any) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return client.request<{ items: Task[]; total: number }>(`/tasks${qs}`);
  },

  getOverdue: () => client.request<Task[]>("/tasks/overdue"),

  create: (data: Partial<Task>) =>
    client.request<Task>("/tasks", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Task>) =>
    client.request<Task>(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};
