import { useEffect, useState } from "react";
import { inputClass } from "../ui/formStyles";
import { listCourses } from "../../services/courses";
import { getCourseAssessmentSummary } from "../../services/reports";
import type { AssessmentSummaryReport, Course, QuestionStat } from "../../types";

export function AssessmentSummaryTab() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseId, setCourseId] = useState("");
  const [summaries, setSummaries] = useState<AssessmentSummaryReport[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    listCourses({ page_size: 100 }).then((page) => setCourses(page.items));
  }, []);

  useEffect(() => {
    if (!courseId) {
      setSummaries([]);
      return;
    }
    setIsLoading(true);
    getCourseAssessmentSummary(courseId)
      .then(setSummaries)
      .finally(() => setIsLoading(false));
  }, [courseId]);

  return (
    <div>
      <select className={`${inputClass} mb-4 max-w-md`} value={courseId} onChange={(e) => setCourseId(e.target.value)}>
        <option value="">Select a course...</option>
        {courses.map((c) => (
          <option key={c.id} value={c.id}>
            {c.title}
          </option>
        ))}
      </select>

      {isLoading && <p className="text-sm text-gray-400">Loading...</p>}
      {!isLoading && courseId && summaries.length === 0 && (
        <p className="text-sm text-gray-500">This course has no assessments.</p>
      )}

      <div className="space-y-6">
        {summaries.map((summary) => (
          <AssessmentCard key={summary.assessment_id} summary={summary} />
        ))}
      </div>
    </div>
  );
}

function AssessmentCard({ summary }: { summary: AssessmentSummaryReport }) {
  return (
    <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <h3 className="text-base font-semibold text-gray-900">{summary.title}</h3>
      <p className="text-xs text-gray-500">
        {summary.module_title ? `Module: ${summary.module_title}` : "Final assessment"} · Passing score{" "}
        {summary.minimum_score}%
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Graded attempts" value={summary.graded_attempts} />
        <Stat label="Students" value={summary.students} />
        <Stat label="Average" value={summary.average_score !== null ? `${summary.average_score}%` : "—"} />
        <Stat label="Passed attempts" value={summary.pass_rate !== null ? `${summary.pass_rate}%` : "—"} />
      </div>

      {summary.graded_attempts === 0 ? (
        <p className="mt-4 text-sm text-gray-400">No graded attempts for this assessment yet.</p>
      ) : (
        <ol className="mt-5 space-y-5">
          {summary.questions.map((question, index) => (
            <QuestionBlock key={question.question_id} index={index + 1} question={question} />
          ))}
        </ol>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg bg-gray-50 px-3 py-2">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-semibold text-gray-900">{value}</p>
    </div>
  );
}

function QuestionBlock({ index, question }: { index: number; question: QuestionStat }) {
  return (
    <li>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="text-sm font-medium text-gray-800">
          {index}. {question.question_text}
        </p>
        <p className="text-xs text-gray-500">
          Answered correctly by {question.correct_percentage}% ({question.correct_count} of {question.total_answers})
        </p>
      </div>
      <div className="mt-2 space-y-1.5">
        {question.options.map((option) => (
          <Bar
            key={option.option_id}
            label={`${option.is_correct ? "✓ " : ""}${option.text}`}
            count={option.count}
            percentage={option.percentage}
            barClass={option.is_correct ? "bg-green-500" : "bg-gray-400"}
          />
        ))}
        {question.unanswered_count > 0 && (
          <Bar
            label="Unanswered"
            count={question.unanswered_count}
            percentage={question.unanswered_percentage}
            barClass="bg-amber-400"
          />
        )}
      </div>
    </li>
  );
}

function Bar({
  label,
  count,
  percentage,
  barClass,
}: {
  label: string;
  count: number;
  percentage: number;
  barClass: string;
}) {
  return (
    <div>
      <div className="flex justify-between gap-3 text-xs text-gray-600">
        <span className="truncate">{label}</span>
        <span className="shrink-0">
          {count} · {percentage}%
        </span>
      </div>
      <div className="mt-0.5 h-2 overflow-hidden rounded-full bg-gray-100">
        <div className={`h-full rounded-full ${barClass}`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
