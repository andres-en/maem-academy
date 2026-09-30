import { api } from "./apiClient";
import type { SystemInfo, User } from "../types";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export function loginWithGoogle(idToken: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/api/v1/auth/google", { id_token: idToken });
}

export function fetchMe(): Promise<User> {
  return api.get<User>("/api/v1/auth/me");
}

export function fetchSystemInfo(): Promise<SystemInfo> {
  return api.get<SystemInfo>("/api/v1/system/info");
}
