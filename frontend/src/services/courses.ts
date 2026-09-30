import { api } from "./apiClient";
import type { Course, CourseDetail, CourseModule, Lesson, LessonContent, Page } from "../types";

export interface ListCoursesParams {
  page?: number;
  page_size?: number;
  status?: string;
  category_id?: string;
  mine?: boolean;
  search?: string;
}

export function listCourses(params: ListCoursesParams = {}): Promise<Page<Course>> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  const qs = query.toString();
  return api.get<Page<Course>>(`/api/v1/courses${qs ? `?${qs}` : ""}`);
}

export function getCourse(id: string): Promise<CourseDetail> {
  return api.get<CourseDetail>(`/api/v1/courses/${id}`);
}

export interface CourseFormData {
  title: string;
  description?: string | null;
  estimated_duration_minutes?: number | null;
  category_ids?: string[];
}

export function createCourse(data: CourseFormData): Promise<CourseDetail> {
  return api.post<CourseDetail>("/api/v1/courses", data);
}

export function updateCourse(id: string, data: CourseFormData): Promise<CourseDetail> {
  return api.put<CourseDetail>(`/api/v1/courses/${id}`, data);
}

export function uploadCoverImage(id: string, file: File): Promise<CourseDetail> {
  const formData = new FormData();
  formData.append("file", file);
  return api.patchForm<CourseDetail>(`/api/v1/courses/${id}/cover-image`, formData);
}

export function addCollaborators(id: string, userIds: string[]): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/collaborators`, { user_ids: userIds });
}

export function removeCollaborator(id: string, userId: string): Promise<CourseDetail> {
  return api.delete<CourseDetail>(`/api/v1/courses/${id}/collaborators/${userId}`);
}

export function submitForReview(id: string): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/submit-review`);
}

export function approveCourse(id: string): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/approve`);
}

export function requestChanges(id: string, comment: string): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/request-changes`, { comment });
}

export function publishCourse(id: string): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/publish`);
}

export function archiveCourse(id: string): Promise<CourseDetail> {
  return api.post<CourseDetail>(`/api/v1/courses/${id}/archive`);
}

export function deleteCourse(id: string): Promise<void> {
  return api.delete<void>(`/api/v1/courses/${id}`);
}

export function forceDeleteCourse(id: string, confirmTitle: string): Promise<void> {
  return api.delete<void>(`/api/v1/courses/${id}/force`, { confirm_title: confirmTitle });
}

// Módulos

export function createModule(courseId: string, data: { title: string; description?: string | null }): Promise<CourseModule> {
  return api.post<CourseModule>(`/api/v1/courses/${courseId}/modules`, data);
}

export function updateModule(moduleId: string, data: { title: string; description?: string | null }): Promise<CourseModule> {
  return api.put<CourseModule>(`/api/v1/course-modules/${moduleId}`, data);
}

export function deleteModule(moduleId: string): Promise<void> {
  return api.delete<void>(`/api/v1/course-modules/${moduleId}`);
}

export function moveModule(moduleId: string, direction: "up" | "down"): Promise<CourseModule> {
  return api.post<CourseModule>(`/api/v1/course-modules/${moduleId}/move`, { direction });
}

// Lecciones

export function createLesson(
  moduleId: string,
  data: { title: string; description?: string | null; completion_type: "MANUAL" | "AUTO" }
): Promise<Lesson> {
  return api.post<Lesson>(`/api/v1/course-modules/${moduleId}/lessons`, data);
}

export function updateLesson(
  lessonId: string,
  data: { title: string; description?: string | null; completion_type: "MANUAL" | "AUTO" }
): Promise<Lesson> {
  return api.put<Lesson>(`/api/v1/lessons/${lessonId}`, data);
}

export function deleteLesson(lessonId: string): Promise<void> {
  return api.delete<void>(`/api/v1/lessons/${lessonId}`);
}

export function moveLesson(lessonId: string, direction: "up" | "down"): Promise<Lesson> {
  return api.post<Lesson>(`/api/v1/lessons/${lessonId}/move`, { direction });
}

// Contenido de lecciones

export interface CreateContentPayload {
  content_type: string;
  title?: string;
  text_content?: string;
  external_url?: string;
  file?: File;
}

export function createContent(lessonId: string, payload: CreateContentPayload): Promise<LessonContent> {
  const formData = new FormData();
  formData.append("content_type", payload.content_type);
  if (payload.title) formData.append("title", payload.title);
  if (payload.text_content) formData.append("text_content", payload.text_content);
  if (payload.external_url) formData.append("external_url", payload.external_url);
  if (payload.file) formData.append("file", payload.file);
  return api.postForm<LessonContent>(`/api/v1/lessons/${lessonId}/contents`, formData);
}

export function updateContent(
  contentId: string,
  data: { title?: string | null; text_content?: string | null; external_url?: string | null }
): Promise<LessonContent> {
  return api.put<LessonContent>(`/api/v1/lesson-contents/${contentId}`, data);
}

export function deleteContent(contentId: string): Promise<void> {
  return api.delete<void>(`/api/v1/lesson-contents/${contentId}`);
}

export function moveContent(contentId: string, direction: "up" | "down"): Promise<LessonContent> {
  return api.post<LessonContent>(`/api/v1/lesson-contents/${contentId}/move`, { direction });
}
