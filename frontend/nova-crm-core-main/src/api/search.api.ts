import { client } from "./client";
import { SearchResults } from "./types";

export const searchApi = {
  global: (query: string) =>
    client.request<SearchResults>(`/search?q=${encodeURIComponent(query)}`),
};
