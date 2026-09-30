import { useEffect, useState } from "react";
import { ApiError } from "../../services/apiClient";
import { getEnrollmentAttempts } from "../../services/reports";
import type { AttemptDetail, EnrollmentAttemptsReport } from "../../types";
import { Modal } from "../ui/Modal";

const ATTEMPT_STATUS_LABELS: Record<string, { label: string; className: string }> = {
  PASSED: { label: "Passed", className: "bg-green-100 text-green-800" },
  FAILED: { label: "Failed", className: "bg-red-100 text-red-800" },
  IN_PROGRESS: { label: "In progress", className: "bg-blue-100 text-blue-800" },
  SUBMITTED: { label: "Submitted", className: "bg-gray-100 text-gray-600" },
};

function formatDateTime(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AttemptsDetailModal({ enrollmentId, onClose }: { enrollmentId: string; onClose: () => void }) {
  const [report, setReport] = useState<EnrollmentAttemptsReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getEnrollmentAttempts(enrollmentId)
      .then(setReport)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load the details."));
  }, [enrollmentId]);

  const title = report ? `${report.user.full_name} — ${report.course.title}` : "Student answers";

  return (
    <Modal title={title} onClose={onClose} widthClass="max-w-3xl">
      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      {!report && !error && <p className="text-sm text-gray-400">Loading...</p>}
      {report && report.assessments.length === 0 && (
        <p className="text-sm text-gray-500">This student has not taken any assessment in this course yet.</p>
      )}
      {report && (
        <div className="space-y-6">
          {report.assessments.map((assessment) => (
            <section key={assessment.assessment_id}>
              <h3 className="text-sm font-semibold text-gray-900">
                {assessment.title}
                <span className="ml-2 text-xs font-normal text-gray-500">
                  {assessment.module_title ? `Module: ${assessment.module_title}` : "Final assessment"} · Passing score{" "}
                  {assessment.minimum_score}%
                </span>
              </h3>
              <div className="mt-2 space-y-2">
                {assessment.attempts.map((attempt, index) => (
                  <AttemptBlock
                    key={attempt.id}
                    attempt={attempt}
                    defaultOpen={index === assessment.attempts.length - 1}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </Modal>
  );
}

function AttemptBlock({ attempt, defaultOpen }: { attempt: AttemptDetail; defaultOpen: boolean }) {
  const status = ATTEMPT_STATUS_LABELS[attempt.status] ?? { label: attempt.status, className: "bg-gray-100 text-gray-600" };

  return (
    <details open={defaultOpen} className="rounded-lg border border-gray-200">
      <summary className="flex cursor-pointer flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2 text-sm">
        <span className="font-medium text-gray-800">Attempt {attempt.attempt_number}</span>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${status.className}`}>{status.label}</span>
        {attempt.score !== null && <span className="text-gray-600">{attempt.score}%</span>}
        <span className="text-xs text-gray-400">{formatDateTime(attempt.submitted_at ?? attempt.started_at)}</span>
      </summary>
      <div className="border-t border-gray-100 px-3 py-2">
        {attempt.answers.length === 0 && <p className="py-1 text-sm text-gray-400">No answers recorded.</p>}
        <ol className="space-y-3">
          {attempt.answers.map((answer, index) => (
            <li key={answer.question_id} className="text-sm">
              <p className="font-medium text-gray-800">
                {index + 1}. {answer.question_text}
              </p>
              <p className={answer.is_correct ? "text-green-700" : "text-red-700"}>
                {answer.is_correct ? "✓" : "✗"} {answer.selected_option_text ?? "Unanswered"}
                <span className="ml-2 text-xs text-gray-400">
                  {answer.points_awarded}/{answer.points} pts
                </span>
              </p>
              {!answer.is_correct && answer.correct_option_text && (
                <p className="text-xs text-gray-500">Correct answer: {answer.correct_option_text}</p>
              )}
            </li>
          ))}
        </ol>
      </div>
    </details>
  );
}
