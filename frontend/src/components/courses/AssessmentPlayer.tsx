import { useEffect, useState } from "react";
import { Button } from "../ui/Button";
import { ApiError } from "../../services/apiClient";
import { listAttempts, startAttempt, submitAttempt } from "../../services/enrollments";
import type { AssessmentStudentSummary, AttemptResult, AttemptSummary, StartAttemptResponse } from "../../types";

export function AssessmentPlayer({
  enrollmentId,
  assessment,
  onChanged,
}: {
  enrollmentId: string;
  assessment: AssessmentStudentSummary;
  onChanged: () => void;
}) {
  const [attemptData, setAttemptData] = useState<StartAttemptResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [history, setHistory] = useState<AttemptSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function loadHistory() {
    try {
      setHistory(await listAttempts(enrollmentId, assessment.id));
    } catch {
      // el historial es informativo
    }
  }

  useEffect(() => {
    setAttemptData(null);
    setResult(null);
    setAnswers({});
    setError(null);
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessment.id]);

  async function handleStart() {
    setError(null);
    setIsBusy(true);
    try {
      const data = await startAttempt(enrollmentId, assessment.id);
      setAttemptData(data);
      setResult(null);
      setAnswers({});
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start the assessment.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSubmit() {
    if (!attemptData) return;
    setError(null);
    setIsBusy(true);
    try {
      const answerList = attemptData.questions.map((q) => ({
        question_id: q.id,
        selected_option_id: answers[q.id] ?? null,
      }));
      const res = await submitAttempt(enrollmentId, attemptData.attempt_id, answerList);
      setResult(res);
      setAttemptData(null);
      await loadHistory();
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not submit the assessment.");
    } finally {
      setIsBusy(false);
    }
  }

  const attemptsRemaining = assessment.max_attempts === null || assessment.attempts_used < assessment.max_attempts;
  const allAnswered = attemptData ? attemptData.questions.every((q) => answers[q.id]) : false;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{assessment.title}</h2>
          <p className="text-xs text-gray-500">
            Passing score: {assessment.minimum_score}% · Attempts: {assessment.attempts_used}/
            {assessment.max_attempts ?? "∞"}
            {assessment.is_required && " · Mandatory"}
          </p>
        </div>
      </div>

      {error && <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      {!attemptData && !result && (
        <div>
          {assessment.best_score !== null && (
            <p className="mb-3 text-sm text-gray-600">
              Mejor puntaje:{" "}
              <span className={assessment.status === "passed" ? "font-semibold text-green-700" : "font-semibold text-red-700"}>
                {assessment.best_score}%
              </span>{" "}
              — {assessment.status === "passed" ? "Passed ✓" : "Failed"}
            </p>
          )}
          {attemptsRemaining ? (
            <Button onClick={handleStart} disabled={isBusy}>
              {assessment.attempts_used > 0 ? "Try again" : "Start assessment"}
            </Button>
          ) : (
            <p className="text-sm text-red-600">You reached the maximum number of attempts.</p>
          )}

          {history.length > 0 && (
            <div className="mt-4">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">Attempt history</p>
              <ul className="space-y-1 text-xs text-gray-500">
                {history.map((h) => (
                  <li key={h.id}>
                    Attempt {h.attempt_number}: {h.status === "IN_PROGRESS" ? "in progress" : `${h.score}% — ${h.status === "PASSED" ? "passed" : "failed"}`}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {attemptData && (
        <div className="space-y-6">
          {attemptData.questions.map((q, index) => (
            <div key={q.id}>
              <p className="text-sm font-medium text-gray-800">
                {index + 1}. {q.question_text}
              </p>
              <div className="mt-2 space-y-1">
                {q.options.map((o) => (
                  <label key={o.id} className="flex items-center gap-2 text-sm text-gray-600">
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      checked={answers[q.id] === o.id}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: o.id }))}
                    />
                    {o.text}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <Button onClick={handleSubmit} disabled={isBusy || !allAnswered}>
            {isBusy ? "Submitting..." : "Submit assessment"}
          </Button>
        </div>
      )}

      {result && (
        <div>
          <div className={`mb-4 rounded-lg px-4 py-3 text-sm font-medium ${result.status === "PASSED" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            Puntaje: {result.score}% — {result.status === "PASSED" ? "Passed! ✓" : "Not passed"}
          </div>
          <div className="space-y-3">
            {result.answers.map((a, index) => (
              <div key={a.question_id} className="rounded-lg bg-gray-50 p-3 text-sm">
                <p className="font-medium text-gray-800">
                  {index + 1}. {a.question_text}
                </p>
                <p className={a.is_correct ? "mt-1 text-xs text-green-700" : "mt-1 text-xs text-red-700"}>
                  {a.is_correct ? "Correct ✓" : "Incorrect ✗"}
                </p>
              </div>
            ))}
          </div>
          {attemptsRemaining && (
            <Button className="mt-4" variant="secondary" onClick={handleStart} disabled={isBusy}>
              Try again
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
