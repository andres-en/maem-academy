import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { AssessmentPlayer } from "../components/courses/AssessmentPlayer";
import { ApiError } from "../services/apiClient";
import { completeLesson, getEnrollmentContent } from "../services/enrollments";
import type { AssessmentStudentSummary, EnrollmentContent, Lesson, LessonContent } from "../types";

type SelectedItem = { type: "lesson"; id: string } | { type: "assessment"; id: string };

function toEmbedUrl(url: string, type: "YOUTUBE" | "VIMEO"): string {
  try {
    const parsed = new URL(url);
    if (type === "YOUTUBE") {
      if (parsed.hostname.includes("youtu.be")) {
        return `https://www.youtube.com/embed/${parsed.pathname.slice(1)}`;
      }
      const id = parsed.searchParams.get("v");
      return id ? `https://www.youtube.com/embed/${id}` : url;
    }
    const id = parsed.pathname.split("/").filter(Boolean).pop();
    return id ? `https://player.vimeo.com/video/${id}` : url;
  } catch {
    return url;
  }
}

function ContentRenderer({ content }: { content: LessonContent }) {
  switch (content.content_type) {
    case "TEXT":
      return <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">{content.text_content}</p>;
    case "IMAGE":
      return content.file_url ? <img src={content.file_url} alt={content.title ?? ""} className="max-w-full rounded-lg" /> : null;
    case "VIDEO":
      return content.file_url ? (
        <video controls className="w-full rounded-lg bg-black" src={content.file_url} />
      ) : null;
    case "AUDIO":
      return content.file_url ? <audio controls className="w-full" src={content.file_url} /> : null;
    case "PDF":
      return content.file_url ? (
        <iframe title={content.title ?? "PDF"} src={content.file_url} className="h-[70vh] w-full rounded-lg border border-gray-200" />
      ) : null;
    case "YOUTUBE":
    case "VIMEO":
      return content.external_url ? (
        <div className="aspect-video w-full overflow-hidden rounded-lg">
          <iframe
            title={content.title ?? content.content_type}
            src={toEmbedUrl(content.external_url, content.content_type)}
            className="h-full w-full border-0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      ) : null;
    case "LINK":
      return content.external_url ? (
        <a href={content.external_url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">
          {content.external_url}
        </a>
      ) : null;
    default:
      return null;
  }
}

export function CoursePlayerPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<EnrollmentContent | null>(null);
  const [selected, setSelected] = useState<SelectedItem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCompleting, setIsCompleting] = useState(false);

  async function refresh() {
    if (!id) return;
    try {
      const data = await getEnrollmentContent(id);
      setContent(data);
      if (!selected) {
        const firstLesson = data.course.modules[0]?.lessons[0];
        if (firstLesson) setSelected({ type: "lesson", id: firstLesson.id });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the course.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const progressByLesson = useMemo(() => {
    const map = new Map<string, string>();
    content?.lesson_progress.forEach((p) => map.set(p.lesson_id, p.status));
    return map;
  }, [content]);

  const allLessons = useMemo(() => {
    const lessons: Lesson[] = [];
    content?.course.modules.forEach((m) => lessons.push(...m.lessons));
    return lessons;
  }, [content]);

  const selectedLesson = selected?.type === "lesson" ? allLessons.find((l) => l.id === selected.id) ?? null : null;
  const selectedAssessment =
    selected?.type === "assessment" ? content?.assessments.find((a) => a.id === selected.id) ?? null : null;

  const moduleAssessments = new Map<string, AssessmentStudentSummary[]>();
  const finalAssessments: AssessmentStudentSummary[] = [];
  (content?.assessments ?? []).forEach((a) => {
    if (a.module_id) {
      moduleAssessments.set(a.module_id, [...(moduleAssessments.get(a.module_id) ?? []), a]);
    } else {
      finalAssessments.push(a);
    }
  });

  async function handleComplete(lessonId: string) {
    if (!id) return;
    setIsCompleting(true);
    try {
      await completeLesson(id, lessonId);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not mark the lesson as completed.");
    } finally {
      setIsCompleting(false);
    }
  }

  useEffect(() => {
    if (!selectedLesson || !id) return;
    if (selectedLesson.completion_type === "AUTO" && progressByLesson.get(selectedLesson.id) !== "COMPLETED") {
      completeLesson(id, selectedLesson.id).then(() => refresh());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLesson?.id]);

  if (isLoading) return <p className="text-sm text-gray-400">Loading...</p>;
  if (error && !content) return <p className="text-sm text-red-600">{error}</p>;
  if (!content) return null;

  const isLessonCompleted = selectedLesson ? progressByLesson.get(selectedLesson.id) === "COMPLETED" : false;

  return (
    <div>
      <button onClick={() => navigate("/mis-cursos")} className="mb-4 text-sm text-gray-500 hover:underline">
        ← Back to my courses
      </button>

      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">{content.course.title}</h1>
          <span className="text-sm font-medium text-gray-500">{content.enrollment.progress_percentage}%</span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-100">
          <div className="h-full bg-brand-600 transition-all" style={{ width: `${content.enrollment.progress_percentage}%` }} />
        </div>
      </div>

      {(content.enrollment.status === "COMPLETED" || content.enrollment.status === "PASSED") && (
        <div className="mb-4 rounded-lg bg-green-50 px-4 py-3 text-sm font-medium text-green-700">
          🎉 Congratulations, you completed this course!
        </div>
      )}
      {content.enrollment.status === "FAILED" && (
        <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          This course was not passed — all attempts of a mandatory assessment were used.
        </div>
      )}
      {error && <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <aside className="lg:col-span-1">
          <div className="rounded-xl border border-gray-200 bg-white p-3">
            {content.course.modules.map((module) => (
              <div key={module.id} className="mb-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">{module.title}</p>
                <ul className="space-y-0.5">
                  {module.lessons.map((lesson) => {
                    const done = progressByLesson.get(lesson.id) === "COMPLETED";
                    return (
                      <li key={lesson.id}>
                        <button
                          onClick={() => setSelected({ type: "lesson", id: lesson.id })}
                          className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm ${
                            selected?.type === "lesson" && selected.id === lesson.id
                              ? "bg-brand-50 text-brand-700"
                              : "text-gray-600 hover:bg-gray-50"
                          }`}
                        >
                          <span className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-[10px] ${done ? "bg-green-500 text-white" : "border border-gray-300 text-transparent"}`}>
                            ✓
                          </span>
                          <span className="truncate">{lesson.title}</span>
                        </button>
                      </li>
                    );
                  })}
                  {(moduleAssessments.get(module.id) ?? []).map((a) => (
                    <AssessmentNavItem key={a.id} assessment={a} selected={selected} onSelect={setSelected} />
                  ))}
                </ul>
              </div>
            ))}
            {finalAssessments.length > 0 && (
              <div className="mb-1 mt-4 border-t border-gray-100 pt-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">Final assessment</p>
                <ul className="space-y-0.5">
                  {finalAssessments.map((a) => (
                    <AssessmentNavItem key={a.id} assessment={a} selected={selected} onSelect={setSelected} />
                  ))}
                </ul>
              </div>
            )}
          </div>
        </aside>

        <main className="lg:col-span-3">
          {selectedLesson && (
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">{selectedLesson.title}</h2>
                  {selectedLesson.description && <p className="text-sm text-gray-500">{selectedLesson.description}</p>}
                </div>
                {selectedLesson.completion_type === "MANUAL" && (
                  <Button disabled={isLessonCompleted || isCompleting} onClick={() => handleComplete(selectedLesson.id)}>
                    {isLessonCompleted ? "Completed ✓" : isCompleting ? "Saving..." : "Mark as completed"}
                  </Button>
                )}
              </div>

              <div className="space-y-6">
                {selectedLesson.contents.length === 0 && <p className="text-sm text-gray-400">This lesson has no content yet.</p>}
                {selectedLesson.contents.map((c) => (
                  <div key={c.id}>
                    {c.title && <p className="mb-2 text-sm font-medium text-gray-700">{c.title}</p>}
                    <ContentRenderer content={c} />
                  </div>
                ))}
              </div>
            </div>
          )}
          {selectedAssessment && id && (
            <AssessmentPlayer enrollmentId={id} assessment={selectedAssessment} onChanged={refresh} />
          )}
          {!selectedLesson && !selectedAssessment && (
            <p className="text-sm text-gray-400">This course has no lessons yet.</p>
          )}
        </main>
      </div>
    </div>
  );
}

function AssessmentNavItem({
  assessment,
  selected,
  onSelect,
}: {
  assessment: AssessmentStudentSummary;
  selected: SelectedItem | null;
  onSelect: (item: SelectedItem) => void;
}) {
  const passed = assessment.status === "passed";
  return (
    <li>
      <button
        onClick={() => onSelect({ type: "assessment", id: assessment.id })}
        className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm ${
          selected?.type === "assessment" && selected.id === assessment.id
            ? "bg-brand-50 text-brand-700"
            : "text-gray-600 hover:bg-gray-50"
        }`}
      >
        <span className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-[10px] ${passed ? "bg-green-500 text-white" : "border border-gray-300 text-transparent"}`}>
          ✓
        </span>
        <span className="truncate">📝 {assessment.title}</span>
      </button>
    </li>
  );
}
