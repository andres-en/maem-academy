import { api } from "./apiClient";
import type { ImportConfirmResponse, ImportPreviewResponse, Page, User, UserDetail } from "../types";

export interface ListUsersParams {
  page?: number;
  page_size?: number;
  role_id?: string;
  status?: string;
  group_id?: string;
  search?: string;
}

export function listUsers(params: ListUsersParams = {}): Promise<Page<User>> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  const qs = query.toString();
  return api.get<Page<User>>(`/api/v1/users${qs ? `?${qs}` : ""}`);
}

export function getUser(id: string): Promise<UserDetail> {
  return api.get<UserDetail>(`/api/v1/users/${id}`);
}

export function createUser(data: {
  full_name: string;
  email: string;
  role_id: string;
  group_ids?: string[];
}): Promise<UserDetail> {
  return api.post<UserDetail>("/api/v1/users", data);
}

export function updateUser(
  id: string,
  data: { full_name: string; role_id: string; group_ids?: string[] }
): Promise<UserDetail> {
  return api.put<UserDetail>(`/api/v1/users/${id}`, data);
}

export function setUserStatus(id: string, status: string): Promise<UserDetail> {
  return api.patch<UserDetail>(`/api/v1/users/${id}/status`, { status });
}

export function deleteUser(id: string): Promise<void> {
  return api.delete<void>(`/api/v1/users/${id}`);
}

export function forceDeleteUser(id: string, confirmEmail: string): Promise<void> {
  return api.delete<void>(`/api/v1/users/${id}/force`, { confirm_email: confirmEmail });
}

export function downloadImportTemplate(): Promise<Blob> {
  return api.get<Blob>("/api/v1/users/import/template");
}

export function validateImport(file: File): Promise<ImportPreviewResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return api.postForm<ImportPreviewResponse>("/api/v1/users/import/validate", formData);
}

export function confirmImport(file: File): Promise<ImportConfirmResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return api.postForm<ImportConfirmResponse>("/api/v1/users/import/confirm", formData);
}
