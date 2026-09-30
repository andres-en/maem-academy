import { api } from "./apiClient";
import type { Category } from "../types";

export function listCategories(status?: string): Promise<Category[]> {
  const query = status ? `?status=${status}` : "";
  return api.get<Category[]>(`/api/v1/categories${query}`);
}

export function createCategory(data: { name: string; description?: string | null }): Promise<Category> {
  return api.post<Category>("/api/v1/categories", data);
}

export function updateCategory(
  id: string,
  data: { name: string; description?: string | null }
): Promise<Category> {
  return api.put<Category>(`/api/v1/categories/${id}`, data);
}

export function setCategoryStatus(id: string, status: string): Promise<Category> {
  return api.patch<Category>(`/api/v1/categories/${id}/status`, { status });
}

export function deleteCategory(id: string): Promise<void> {
  return api.delete<void>(`/api/v1/categories/${id}`);
}
