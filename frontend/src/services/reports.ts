import { api } from "./apiClient";
import type {
  AssessmentSummaryReport,
  CourseReportRow,
  EnrollmentAttemptsReport,
  ReportSummary,
  UserReportRow,
} from "../types";

export function getReportSummary(): Promise<ReportSummary> {
  return api.get<ReportSummary>("/api/v1/reports/summary");
}

export function getCourseReport(courseId: string): Promise<CourseReportRow[]> {
  return api.get<CourseReportRow[]>(`/api/v1/reports/courses/${courseId}`);
}

export function getUserReport(userId: string): Promise<UserReportRow[]> {
  return api.get<UserReportRow[]>(`/api/v1/reports/users/${userId}`);
}

export function getEnrollmentAttempts(enrollmentId: string): Promise<EnrollmentAttemptsReport> {
  return api.get<EnrollmentAttemptsReport>(`/api/v1/reports/enrollments/${enrollmentId}/attempts`);
}

export function getCourseAssessmentSummary(courseId: string): Promise<AssessmentSummaryReport[]> {
  return api.get<AssessmentSummaryReport[]>(`/api/v1/reports/courses/${courseId}/assessment-summary`);
}
