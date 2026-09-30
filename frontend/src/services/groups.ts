import { api } from "./apiClient";
import type { Group, GroupDetail } from "../types";

export function listGroups(status?: string): Promise<Group[]> {
  const query = status ? `?status=${status}` : "";
  return api.get<Group[]>(`/api/v1/groups${query}`);
}

export function getGroup(id: string): Promise<GroupDetail> {
  return api.get<GroupDetail>(`/api/v1/groups/${id}`);
}

export function createGroup(data: {
  name: string;
  description?: string | null;
  user_ids?: string[];
}): Promise<GroupDetail> {
  return api.post<GroupDetail>("/api/v1/groups", data);
}

export function updateGroup(id: string, data: { name: string; description?: string | null }): Promise<GroupDetail> {
  return api.put<GroupDetail>(`/api/v1/groups/${id}`, data);
}

export function setGroupStatus(id: string, status: string): Promise<GroupDetail> {
  return api.patch<GroupDetail>(`/api/v1/groups/${id}/status`, { status });
}

export function deleteGroup(id: string): Promise<void> {
  return api.delete<void>(`/api/v1/groups/${id}`);
}

export function addGroupUsers(id: string, userIds: string[]): Promise<GroupDetail> {
  return api.post<GroupDetail>(`/api/v1/groups/${id}/users`, { user_ids: userIds });
}

export function removeGroupUser(id: string, userId: string): Promise<GroupDetail> {
  return api.delete<GroupDetail>(`/api/v1/groups/${id}/users/${userId}`);
}
