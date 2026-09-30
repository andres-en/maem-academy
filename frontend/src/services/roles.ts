import { api } from "./apiClient";
import type { Role } from "../types";

export function listRoles(): Promise<Role[]> {
  return api.get<Role[]>("/api/v1/roles");
}
