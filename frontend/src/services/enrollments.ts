import { api } from "./apiClient";
import type {
  AssignmentCreateResponse,
  AttemptResult,
  AttemptSummary,
  CourseAssignment,
  Enrollment,
  EnrollmentContent,
  EnrollmentCreateResponse,
  LessonCompleteResponse,
  Page,
  StartAttemptResponse,
} from "../types";

export interface CreateAssignmentPayload {
  user_ids?: string[];
  group_ids?: string[];
  is_required: boolean;
  due_date?: string | null;
  overdue_action: "ALLOW_CONTINUE" | "BLOCK";
}

export function createAssignment(courseId: string, payload: CreateAssignmentPayload): Promise<AssignmentCreateResponse> {
  return api.post<AssignmentCreateResponse>(`/api/v1/courses/${courseId}/assignments`, payload);
}

export function listAssignments(courseId: string): Promise<CourseAssignment[]> {
  return api.get<CourseAssignment[]>(`/api/v1/courses/${courseId}/assignments`);
}

export interface CreateEnrollmentsPayload {
  user_ids: string[];
  is_required?: boolean;
  due_date?: string | null;
}

export function createEnrollments(courseId: string, payload: CreateEnrollmentsPayload): Promise<EnrollmentCreateResponse> {
  return api.post<EnrollmentCreateResponse>(`/api/v1/courses/${courseId}/enrollments`, payload);
}

export function listCourseEnrollments(courseId: string, page = 1, pageSize = 50): Promise<Page<Enrollment>> {
  return api.get<Page<Enrollment>>(`/api/v1/courses/${courseId}/enrollments?page=${page}&page_size=${pageSize}`);
}

export function listMyEnrollments(): Promise<Enrollment[]> {
  return api.get<Enrollment[]>("/api/v1/enrollments/me");
}

export function listUserEnrollments(userId: string): Promise<Enrollment[]> {
  return api.get<Enrollment[]>(`/api/v1/users/${userId}/enrollments`);
}

export function updateEnrollmentDueDate(enrollmentId: string, dueDate: string | null): Promise<Enrollment> {
  return api.patch<Enrollment>(`/api/v1/enrollments/${enrollmentId}`, { due_date: dueDate });
}

export function cancelEnrollment(enrollmentId: string): Promise<Enrollment> {
  return api.post<Enrollment>(`/api/v1/enrollments/${enrollmentId}/cancel`);
}

export function getEnrollmentContent(enrollmentId: string): Promise<EnrollmentContent> {
  return api.get<EnrollmentContent>(`/api/v1/enrollments/${enrollmentId}/content`);
}

export function completeLesson(enrollmentId: string, lessonId: string): Promise<LessonCompleteResponse> {
  return api.post<LessonCompleteResponse>(`/api/v1/enrollments/${enrollmentId}/lessons/${lessonId}/complete`);
}

export function startAttempt(enrollmentId: string, assessmentId: string): Promise<StartAttemptResponse> {
  return api.post<StartAttemptResponse>(`/api/v1/enrollments/${enrollmentId}/assessments/${assessmentId}/start`);
}

export function submitAttempt(
  enrollmentId: string,
  attemptId: string,
  answers: { question_id: string; selected_option_id: string | null }[]
): Promise<AttemptResult> {
  return api.post<AttemptResult>(`/api/v1/enrollments/${enrollmentId}/attempts/${attemptId}/submit`, { answers });
}

export function listAttempts(enrollmentId: string, assessmentId: string): Promise<AttemptSummary[]> {
  return api.get<AttemptSummary[]>(`/api/v1/enrollments/${enrollmentId}/assessments/${assessmentId}/attempts`);
}
