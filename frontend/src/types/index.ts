export interface Role {
  id: string;
  name: string;
  display_name: string;
  description: string | null;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  status: "ACTIVE" | "INACTIVE";
  role: Role;
  last_login_at: string | null;
  created_at: string;
}

export interface UserDetail extends User {
  groups: Group[];
}

export interface Group {
  id: string;
  name: string;
  description: string | null;
  status: "ACTIVE" | "INACTIVE";
  created_at: string;
  member_count: number;
}

export interface GroupMember {
  id: string;
  full_name: string;
  email: string;
}

export interface GroupDetail extends Group {
  members: GroupMember[];
}

export interface Category {
  id: string;
  name: string;
  description: string | null;
  status: "ACTIVE" | "INACTIVE";
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ImportRowResult {
  row_number: number;
  full_name: string | null;
  email: string | null;
  role: string | null;
  groups: string[];
  errors: string[];
}

export interface ImportPreviewResponse {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  rows: ImportRowResult[];
}

export interface ImportConfirmResponse {
  created: number;
  skipped: number;
  rows: ImportRowResult[];
}

export interface SystemInfo {
  environment: string;
  google_oauth_enabled: boolean;
}

export type CourseStatus = "DRAFT" | "IN_REVIEW" | "CHANGES_REQUESTED" | "APPROVED" | "PUBLISHED" | "ARCHIVED";

export interface UserBrief {
  id: string;
  full_name: string;
  email: string;
}

export type ContentType = "TEXT" | "VIDEO" | "PDF" | "IMAGE" | "AUDIO" | "YOUTUBE" | "VIMEO" | "LINK";

export interface LessonContent {
  id: string;
  lesson_id: string;
  content_type: ContentType;
  title: string | null;
  position: number;
  text_content: string | null;
  external_url: string | null;
  file_url: string | null;
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  description: string | null;
  position: number;
  completion_type: "MANUAL" | "AUTO";
  contents: LessonContent[];
}

export interface CourseModule {
  id: string;
  course_id: string;
  title: string;
  description: string | null;
  position: number;
  lessons: Lesson[];
}

export interface Course {
  id: string;
  title: string;
  description: string | null;
  cover_image_url: string | null;
  estimated_duration_minutes: number | null;
  status: CourseStatus;
  owner: UserBrief;
  categories: Category[];
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CourseDetail extends Course {
  collaborators: UserBrief[];
  reviewed_by: UserBrief | null;
  review_comment: string | null;
  reviewed_at: string | null;
  modules: CourseModule[];
}

export interface CourseBrief {
  id: string;
  title: string;
  cover_image_url: string | null;
  status: CourseStatus;
}

export interface GroupBrief {
  id: string;
  name: string;
}

export type OverdueAction = "ALLOW_CONTINUE" | "BLOCK";

export interface CourseAssignment {
  id: string;
  course_id: string;
  is_required: boolean;
  due_date: string | null;
  overdue_action: OverdueAction;
  status: "ACTIVE" | "INACTIVE";
  created_by: UserBrief;
  created_at: string;
  target_users: UserBrief[];
  target_groups: GroupBrief[];
}

export type EnrollmentType = "ASSIGNMENT" | "MANUAL" | "RETAKE";
export type EnrollmentStatus =
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "PASSED"
  | "FAILED"
  | "OVERDUE"
  | "BLOCKED"
  | "CANCELLED";

export interface Enrollment {
  id: string;
  user: UserBrief;
  course: CourseBrief;
  assignment_id: string | null;
  enrollment_type: EnrollmentType;
  status: EnrollmentStatus;
  is_required: boolean;
  assigned_at: string;
  started_at: string | null;
  due_date: string | null;
  completed_at: string | null;
}

export interface AssignmentCreateResponse {
  assignment: CourseAssignment;
  enrollments_created: number;
  enrollments_skipped: number;
}

export interface EnrollmentCreateResponse {
  created: number;
  skipped: number;
  enrollments: Enrollment[];
}

export interface LessonProgress {
  lesson_id: string;
  status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED";
  progress_percentage: number;
  completed_at: string | null;
}

export interface EnrollmentSummary {
  id: string;
  status: EnrollmentStatus;
  progress_percentage: number;
  is_required: boolean;
  due_date: string | null;
  overdue_action: OverdueAction;
  started_at: string | null;
  completed_at: string | null;
}

export type AssessmentStudentStatus = "not_started" | "in_progress" | "passed" | "failed";

export interface AssessmentStudentSummary {
  id: string;
  title: string;
  module_id: string | null;
  minimum_score: number;
  max_attempts: number | null;
  is_required: boolean;
  attempts_used: number;
  best_score: number | null;
  status: AssessmentStudentStatus;
}

export interface EnrollmentContent {
  enrollment: EnrollmentSummary;
  course: CourseDetail;
  lesson_progress: LessonProgress[];
  assessments: AssessmentStudentSummary[];
}

export interface LessonCompleteResponse {
  lesson_progress: LessonProgress;
  enrollment: EnrollmentSummary;
}

// Autoría de evaluaciones (Admin/Instructor)

export interface QuestionOption {
  id: string;
  text: string;
  is_correct: boolean;
  position: number;
}

export interface Question {
  id: string;
  question_text: string;
  points: number;
  position: number;
  options: QuestionOption[];
}

export interface Assessment {
  id: string;
  course_id: string;
  module_id: string | null;
  title: string;
  description: string | null;
  minimum_score: number;
  max_attempts: number | null;
  is_required: boolean;
  questions: Question[];
}

// Resolución de evaluaciones (Estudiante)

export interface AttemptOption {
  id: string;
  text: string;
}

export interface AttemptQuestion {
  id: string;
  question_text: string;
  points: number;
  options: AttemptOption[];
}

export interface StartAttemptResponse {
  attempt_id: string;
  attempt_number: number;
  status: string;
  questions: AttemptQuestion[];
}

export interface AttemptAnswerResult {
  question_id: string;
  question_text: string;
  selected_option_id: string | null;
  correct_option_id: string | null;
  is_correct: boolean;
  points_awarded: number;
}

export interface AttemptResult {
  attempt_id: string;
  attempt_number: number;
  score: number;
  status: "PASSED" | "FAILED";
  submitted_at: string | null;
  answers: AttemptAnswerResult[];
}

export interface AttemptSummary {
  id: string;
  attempt_number: number;
  score: number | null;
  status: string;
  started_at: string;
  submitted_at: string | null;
}

// Reportes

export interface ReportSummary {
  active_users: number;
  published_courses: number;
  courses_in_review: number;
  enrollments_total: number;
  pending: number;
  in_progress: number;
  completed: number;
  passed: number;
  failed: number;
  overdue: number;
  cancelled: number;
}

export interface CourseReportRow {
  enrollment_id: string;
  user: UserBrief;
  status: EnrollmentStatus;
  progress_percentage: number;
  score: number | null;
  is_required: boolean;
  assigned_at: string;
  due_date: string | null;
  completed_at: string | null;
}

export interface UserReportRow {
  enrollment_id: string;
  course: CourseBrief;
  status: EnrollmentStatus;
  progress_percentage: number;
  score: number | null;
  is_required: boolean;
  assigned_at: string;
  due_date: string | null;
  completed_at: string | null;
}

export interface AttemptAnswerDetail {
  question_id: string;
  question_text: string;
  points: number;
  selected_option_text: string | null;
  correct_option_text: string | null;
  is_correct: boolean;
  points_awarded: number;
}

export interface AttemptDetail {
  id: string;
  attempt_number: number;
  score: number | null;
  status: string;
  started_at: string;
  submitted_at: string | null;
  answers: AttemptAnswerDetail[];
}

export interface AssessmentAttemptsDetail {
  assessment_id: string;
  title: string;
  module_title: string | null;
  minimum_score: number;
  attempts: AttemptDetail[];
}

export interface EnrollmentAttemptsReport {
  user: UserBrief;
  course: CourseBrief;
  assessments: AssessmentAttemptsDetail[];
}

export interface OptionStat {
  option_id: string;
  text: string;
  is_correct: boolean;
  count: number;
  percentage: number;
}

export interface QuestionStat {
  question_id: string;
  question_text: string;
  points: number;
  total_answers: number;
  correct_count: number;
  correct_percentage: number;
  unanswered_count: number;
  unanswered_percentage: number;
  options: OptionStat[];
}

export interface AssessmentSummaryReport {
  assessment_id: string;
  title: string;
  module_title: string | null;
  minimum_score: number;
  graded_attempts: number;
  students: number;
  average_score: number | null;
  pass_rate: number | null;
  questions: QuestionStat[];
}
