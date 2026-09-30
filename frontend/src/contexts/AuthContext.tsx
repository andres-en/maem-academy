import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchMe, fetchSystemInfo, loginWithGoogle } from "../services/auth";
import { getToken, setToken } from "../services/apiClient";
import type { SystemInfo, User } from "../types";

interface AuthContextValue {
  user: User | null;
  systemInfo: SystemInfo | null;
  isLoading: boolean;
  loginGoogle: (idToken: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const info = await fetchSystemInfo();
        if (!cancelled) setSystemInfo(info);
      } catch {
        // backend not reachable yet; keep systemInfo null
      }

      if (getToken()) {
        try {
          const me = await fetchMe();
          if (!cancelled) setUser(me);
        } catch {
          setToken(null);
        }
      }
      if (!cancelled) setIsLoading(false);
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const loginGoogle = useCallback(async (idToken: string) => {
    const result = await loginWithGoogle(idToken);
    setToken(result.access_token);
    setUser(result.user);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const hasRole = useCallback(
    (...roles: string[]) => !!user && roles.includes(user.role.name),
    [user]
  );

  const value = useMemo(
    () => ({ user, systemInfo, isLoading, loginGoogle, logout, hasRole }),
    [user, systemInfo, isLoading, loginGoogle, logout, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
