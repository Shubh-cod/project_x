import { client } from "./client";
import { TokenPair, User } from "./types";

export const authApi = {
  login: (email: string, password: string) =>
    client.request<{ user: User; tokens: TokenPair }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (email: string, password: string, full_name: string) =>
    client.request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),

  logout: () => client.request("/auth/logout", { method: "POST" }),

  getMe: () => client.request<User>("/auth/me"),
  
  updateMe: (data: Partial<User>) => client.request<User>("/auth/me", { method: "PATCH", body: JSON.stringify(data) }),
  
  changePassword: (data: any) => client.request("/auth/change-password", { method: "POST", body: JSON.stringify(data) }),
};
