import { api } from "./apiClient";
import type { Assessment, Question } from "../types";

export interface AssessmentFormData {
  module_id?: string | null;
  title: string;
  description?: string | null;
  minimum_score: number;
  max_attempts?: number | null;
  is_required: boolean;
}

export function listCourseAssessments(courseId: string): Promise<Assessment[]> {
  return api.get<Assessment[]>(`/api/v1/courses/${courseId}/assessments`);
}

export function createAssessment(courseId: string, data: AssessmentFormData): Promise<Assessment> {
  return api.post<Assessment>(`/api/v1/courses/${courseId}/assessments`, data);
}

export function updateAssessment(assessmentId: string, data: Omit<AssessmentFormData, "module_id">): Promise<Assessment> {
  return api.put<Assessment>(`/api/v1/assessments/${assessmentId}`, data);
}

export function deleteAssessment(assessmentId: string): Promise<void> {
  return api.delete<void>(`/api/v1/assessments/${assessmentId}`);
}

export interface QuestionFormData {
  question_text: string;
  points: number;
  options: { text: string; is_correct: boolean }[];
}

export function createQuestion(assessmentId: string, data: QuestionFormData): Promise<Question> {
  return api.post<Question>(`/api/v1/assessments/${assessmentId}/questions`, data);
}

export function updateQuestion(questionId: string, data: QuestionFormData): Promise<Question> {
  return api.put<Question>(`/api/v1/questions/${questionId}`, data);
}

export function deleteQuestion(questionId: string): Promise<void> {
  return api.delete<void>(`/api/v1/questions/${questionId}`);
}
