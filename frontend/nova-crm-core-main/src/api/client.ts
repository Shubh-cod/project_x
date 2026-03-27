import { TokenPair } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private getTokens(): TokenPair | null {
    const access = localStorage.getItem("access_token");
    const refresh = localStorage.getItem("refresh_token");
    if (!access || !refresh) return null;
    return { access_token: access, refresh_token: refresh };
  }

  setTokens(tokens: TokenPair) {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
  }

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const tokens = this.getTokens();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (tokens) {
      headers["Authorization"] = `Bearer ${tokens.access_token}`;
    }

    const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

    if (res.status === 401 && tokens) {
      // Try refresh
      const refreshRes = await fetch(`${BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      });
      if (refreshRes.ok) {
        const body = await refreshRes.json();
        // Backend returns APIResponse which has data field
        const newTokens = body.data as TokenPair;
        this.setTokens(newTokens);
        headers["Authorization"] = `Bearer ${newTokens.access_token}`;
        const retry = await fetch(`${BASE_URL}${path}`, { ...options, headers });
        if (!retry.ok) throw new Error(`API Error: ${retry.status}`);
        const retryBody = await retry.json();
        return retryBody.data as T;
      } else {
        this.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = "/login";
        }
        throw new Error("Session expired");
      }
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.detail || `API Error: ${res.status}`);
    }
    
    if (res.status === 204) return {} as T;
    
    const body = await res.json();
    // Assuming backend always wraps in APIResponse { success: bool, data: T, message: string }
    return body.data as T;
  }
}

export const client = new ApiClient();
