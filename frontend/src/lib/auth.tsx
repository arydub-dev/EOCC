"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  clearToken,
  getToken,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  setTokens,
} from "@/lib/api";
import type { Organization, TokenResponse, User } from "@/lib/types";

interface AuthState {
  user: User | null;
  organization: Organization | null;
  permissions: string[];
  loading: boolean;
  login: (email: string, password: string, rememberMe?: boolean, mfaCode?: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
  setOrganization: (org: Organization | null) => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  async function loadSession() {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const me = await api<User>("/auth/me");
      setUser(me);
      setPermissions(me.permissions ?? []);
      if (me.organization_id) {
        try {
          const ws = await api<{ organization: Organization }>("/workspace");
          setOrganization(ws.organization);
        } catch {
          /* workspace not ready */
        }
      }
    } catch {
      clearToken();
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function applyToken(res: TokenResponse) {
    setTokens(res.access_token, res.refresh_token ?? null);
    setUser(res.user);
    setPermissions(res.permissions ?? []);
    setOrganization(res.organization ?? null);
    if (res.needs_onboarding) {
      router.push("/onboarding");
    } else {
      router.push("/app");
    }
  }

  async function login(email: string, password: string, rememberMe = false, mfaCode?: string) {
    const res = (await apiLogin(email, password, rememberMe, mfaCode)) as TokenResponse;
    applyToken(res);
  }

  async function register(email: string, password: string, fullName: string) {
    const res = (await apiRegister(email, password, fullName)) as TokenResponse;
    applyToken(res);
  }

  async function logout() {
    await apiLogout();
    setUser(null);
    setOrganization(null);
    setPermissions([]);
    router.push("/login");
  }

  async function refresh() {
    await loadSession();
  }

  function hasPermission(permission: string): boolean {
    return permissions.includes(permission);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        organization,
        permissions,
        loading,
        login,
        register,
        logout,
        refresh,
        setOrganization,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
