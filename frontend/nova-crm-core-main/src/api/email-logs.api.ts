import { client } from "./client";
import { EmailLog } from "./types";

export const emailLogsApi = {
  create: (data: { subject: string; body_preview?: string; contact_id: string }) =>
    client.request<EmailLog>("/email-logs", { method: "POST", body: JSON.stringify(data) }),

  listByContact: (contactId: string, limit = 50) =>
    client.request<EmailLog[]>(`/email-logs/contact/${contactId}?limit=${limit}`),

  get: (id: string) => client.request<EmailLog>(`/email-logs/${id}`),
};
