import * as React from "react";
import { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/api/types";
import { authApi } from "@/api/auth.api";
import { client } from "@/api/client";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      const accessToken = localStorage.getItem("access_token");
      if (accessToken) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
        } catch (err) {
          console.error("Auth init failed", err);
          client.clearTokens();
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = async (email: string, password: string) => {
    const { user, tokens } = await authApi.login(email, password);
    client.setTokens(tokens);
    setUser(user);
  };

  const register = async (email: string, password: string, fullName: string) => {
    await authApi.register(email, password, fullName);
  };

  const logout = () => {
    authApi.logout().catch(console.error);
    client.clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
