import { client } from "./client";
import { Activity, PaginatedResponse } from "./types";

export const activitiesApi = {
  listByEntity: (entityType: string, entityId: string, page = 1, pageSize = 20) =>
    client.request<PaginatedResponse<Activity>>(
      `/activities/entity/${entityType}/${entityId}?page=${page}&page_size=${pageSize}`
    ),

  listGlobal: (params?: {
    user_id?: string;
    entity_type?: string;
    page?: number;
    page_size?: number;
  }) => {
    const qs = params ? "?" + new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]))
    ).toString() : "";
    return client.request<PaginatedResponse<Activity>>(`/activities${qs}`);
  },
};
