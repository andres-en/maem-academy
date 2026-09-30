import { useEffect, useState } from "react";
import { Button } from "../ui/Button";
import { Modal } from "../ui/Modal";
import { inputClass, labelClass } from "../ui/formStyles";
import { ApiError } from "../../services/apiClient";
import {
  createAssessment,
  createQuestion,
  deleteAssessment,
  deleteQuestion,
  listCourseAssessments,
  updateAssessment,
  updateQuestion,
} from "../../services/assessments";
import type { Assessment, CourseDetail, Question } from "../../types";

export function AssessmentSection({
  course,
  canEdit,
}: {
  course: CourseDetail;
  canEdit: boolean;
}) {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Assessment | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setAssessments(await listCourseAssessments(course.id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the assessments.");
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [course.id]);

  function moduleLabel(moduleId: string | null): string {
    if (!moduleId) return "Course final assessment";
    const module = course.modules.find((m) => m.id === moduleId);
    return module ? `Module: ${module.title}` : "Module";
  }

  async function handleDelete(assessment: Assessment) {
    if (!confirm(`Delete the assessment "${assessment.title}" and all its questions?`)) return;
    try {
      await deleteAssessment(assessment.id);
      refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete the assessment.");
    }
  }

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Assessments</h2>
        {canEdit && <Button onClick={() => setShowCreate(true)}>New assessment</Button>}
      </div>

      {error && <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="mt-4 space-y-4">
        {assessments.length === 0 && <p className="text-sm text-gray-400">This course has no assessments yet.</p>}
        {assessments.map((assessment) => (
          <div key={assessment.id} className="rounded-xl border border-gray-200 bg-white p-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-brand-600">
                  {moduleLabel(assessment.module_id)}
                </span>
                <h3 className="mt-1 text-sm font-semibold text-gray-900">{assessment.title}</h3>
                <p className="text-xs text-gray-400">
                  Passing score: {assessment.minimum_score}% · Attempts: {assessment.max_attempts ?? "unlimited"} ·{" "}
                  {assessment.is_required ? "Mandatory" : "Optional"}
                </p>
              </div>
              {canEdit && (
                <div className="flex gap-3 text-xs">
                  <button className="text-brand-600 hover:underline" onClick={() => setEditing(assessment)}>
                    Edit
                  </button>
                  <button className="text-red-600 hover:underline" onClick={() => handleDelete(assessment)}>
                    Delete
                  </button>
                </div>
              )}
            </div>

            <QuestionList assessment={assessment} canEdit={canEdit} onChanged={refresh} onError={setError} />
          </div>
        ))}
      </div>

      {showCreate && (
        <AssessmentFormModal
          course={course}
          assessment={null}
          onClose={() => setShowCreate(false)}
          onSaved={() => {
            setShowCreate(false);
            refresh();
          }}
        />
      )}
      {editing && (
        <AssessmentFormModal
          course={course}
          assessment={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            refresh();
          }}
        />
      )}
    </div>
  );
}

function QuestionList({
  assessment,
  canEdit,
  onChanged,
  onError,
}: {
  assessment: Assessment;
  canEdit: boolean;
  onChanged: () => void;
  onError: (m: string) => void;
}) {
  const [showAdd, setShowAdd] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);

  async function handleDelete(question: Question) {
    if (!confirm("Delete this question?")) return;
    try {
      await deleteQuestion(question.id);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not delete the question.");
    }
  }

  return (
    <div className="mt-3 space-y-2 border-t border-gray-100 pt-3">
      {assessment.questions.length === 0 && <p className="text-xs text-gray-400">No questions yet.</p>}
      {assessment.questions.map((q, index) => (
        <div key={q.id} className="rounded-lg bg-gray-50 p-3 text-sm">
          <div className="flex items-start justify-between">
            <p className="font-medium text-gray-800">
              {index + 1}. {q.question_text} <span className="text-xs text-gray-400">({q.points} pts)</span>
            </p>
            {canEdit && (
              <div className="flex gap-2 text-xs">
                <button className="text-brand-600 hover:underline" onClick={() => setEditingQuestion(q)}>
                  Edit
                </button>
                <button className="text-red-600 hover:underline" onClick={() => handleDelete(q)}>
                  Delete
                </button>
              </div>
            )}
          </div>
          <ul className="mt-1 space-y-0.5 pl-4 text-xs text-gray-500">
            {q.options.map((o) => (
              <li key={o.id} className={o.is_correct ? "font-medium text-green-700" : ""}>
                {o.is_correct ? "✓ " : "· "}
                {o.text}
              </li>
            ))}
          </ul>
        </div>
      ))}
      {canEdit && (
        <button className="text-xs text-brand-600 hover:underline" onClick={() => setShowAdd(true)}>
          + Add question
        </button>
      )}

      {showAdd && (
        <QuestionFormModal
          assessmentId={assessment.id}
          question={null}
          onClose={() => setShowAdd(false)}
          onSaved={() => {
            setShowAdd(false);
            onChanged();
          }}
        />
      )}
      {editingQuestion && (
        <QuestionFormModal
          assessmentId={assessment.id}
          question={editingQuestion}
          onClose={() => setEditingQuestion(null)}
          onSaved={() => {
            setEditingQuestion(null);
            onChanged();
          }}
        />
      )}
    </div>
  );
}

function AssessmentFormModal({
  course,
  assessment,
  onClose,
  onSaved,
}: {
  course: CourseDetail;
  assessment: Assessment | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [title, setTitle] = useState(assessment?.title ?? "");
  const [moduleId, setModuleId] = useState(assessment?.module_id ?? "");
  const [minimumScore, setMinimumScore] = useState(String(assessment?.minimum_score ?? 70));
  const [unlimited, setUnlimited] = useState(assessment ? assessment.max_attempts === null : true);
  const [maxAttempts, setMaxAttempts] = useState(assessment?.max_attempts ? String(assessment.max_attempts) : "3");
  const [isRequired, setIsRequired] = useState(assessment?.is_required ?? true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const payload = {
        title,
        minimum_score: Number(minimumScore),
        max_attempts: unlimited ? null : Number(maxAttempts),
        is_required: isRequired,
      };
      if (assessment) {
        await updateAssessment(assessment.id, payload);
      } else {
        await createAssessment(course.id, { ...payload, module_id: moduleId || null });
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save the assessment.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title={assessment ? "Edit assessment" : "New assessment"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <div>
          <label className={labelClass}>Title</label>
          <input required value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />
        </div>
        {!assessment && (
          <div>
            <label className={labelClass}>Scope</label>
            <select className={inputClass} value={moduleId} onChange={(e) => setModuleId(e.target.value)}>
              <option value="">Course final assessment</option>
              {course.modules.map((m) => (
                <option key={m.id} value={m.id}>
                  Module: {m.title}
                </option>
              ))}
            </select>
          </div>
        )}
        <div>
          <label className={labelClass}>Passing score (%)</label>
          <input
            type="number"
            min={0}
            max={100}
            required
            value={minimumScore}
            onChange={(e) => setMinimumScore(e.target.value)}
            className={`${inputClass} max-w-[8rem]`}
          />
        </div>
        <div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={unlimited} onChange={(e) => setUnlimited(e.target.checked)} />
            Unlimited attempts
          </label>
          {!unlimited && (
            <input
              type="number"
              min={1}
              value={maxAttempts}
              onChange={(e) => setMaxAttempts(e.target.value)}
              className={`${inputClass} mt-2 max-w-[8rem]`}
            />
          )}
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={isRequired} onChange={(e) => setIsRequired(e.target.checked)} />
          Required to complete the course
        </label>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function QuestionFormModal({
  assessmentId,
  question,
  onClose,
  onSaved,
}: {
  assessmentId: string;
  question: Question | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [text, setText] = useState(question?.question_text ?? "");
  const [points, setPoints] = useState(String(question?.points ?? 1));
  const [options, setOptions] = useState<{ text: string; is_correct: boolean }[]>(
    question?.options.map((o) => ({ text: o.text, is_correct: o.is_correct })) ?? [
      { text: "", is_correct: true },
      { text: "", is_correct: false },
    ]
  );
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateOptionText(index: number, value: string) {
    setOptions((prev) => prev.map((o, i) => (i === index ? { ...o, text: value } : o)));
  }

  function setCorrect(index: number) {
    setOptions((prev) => prev.map((o, i) => ({ ...o, is_correct: i === index })));
  }

  function addOption() {
    setOptions((prev) => [...prev, { text: "", is_correct: false }]);
  }

  function removeOption(index: number) {
    setOptions((prev) => {
      const next = prev.filter((_, i) => i !== index);
      if (!next.some((o) => o.is_correct) && next.length > 0) next[0].is_correct = true;
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (options.length < 2) {
      setError("At least 2 options are required.");
      return;
    }
    if (!options.some((o) => o.is_correct)) {
      setError("Mark which option is correct.");
      return;
    }
    setIsSubmitting(true);
    try {
      const payload = { question_text: text, points: Number(points), options };
      if (question) {
        await updateQuestion(question.id, payload);
      } else {
        await createQuestion(assessmentId, payload);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save the question.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title={question ? "Edit question" : "New question"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <div>
          <label className={labelClass}>Question</label>
          <textarea required className={inputClass} rows={2} value={text} onChange={(e) => setText(e.target.value)} />
        </div>
        <div>
          <label className={labelClass}>Points</label>
          <input
            type="number"
            min={0.1}
            step={0.1}
            required
            value={points}
            onChange={(e) => setPoints(e.target.value)}
            className={`${inputClass} max-w-[8rem]`}
          />
        </div>
        <div>
          <label className={labelClass}>Options (mark the correct one)</label>
          <div className="space-y-2">
            {options.map((option, index) => (
              <div key={index} className="flex items-center gap-2">
                <input type="radio" name="correct-option" checked={option.is_correct} onChange={() => setCorrect(index)} />
                <input
                  required
                  className={inputClass}
                  placeholder={`Option ${index + 1}`}
                  value={option.text}
                  onChange={(e) => updateOptionText(index, e.target.value)}
                />
                {options.length > 2 && (
                  <button type="button" className="text-xs text-red-600 hover:underline" onClick={() => removeOption(index)}>
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
          <button type="button" className="mt-2 text-xs text-brand-600 hover:underline" onClick={addOption}>
            + Add option
          </button>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
