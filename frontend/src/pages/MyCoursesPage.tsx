import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { listMyEnrollments } from "../services/enrollments";
import type { Enrollment, EnrollmentStatus } from "../types";

const STATUS_LABELS: Record<EnrollmentStatus, string> = {
  ASSIGNED: "Pending",
  IN_PROGRESS: "In progress",
  COMPLETED: "Completed",
  PASSED: "Passed",
  FAILED: "Failed",
  OVERDUE: "Overdue",
  BLOCKED: "Blocked",
  CANCELLED: "Cancelled",
};

const STATUS_COLORS: Record<EnrollmentStatus, string> = {
  ASSIGNED: "bg-gray-100 text-gray-600",
  IN_PROGRESS: "bg-blue-100 text-blue-800",
  COMPLETED: "bg-green-100 text-green-800",
  PASSED: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
  OVERDUE: "bg-amber-100 text-amber-800",
  BLOCKED: "bg-red-100 text-red-800",
  CANCELLED: "bg-gray-200 text-gray-500",
};

const FILTERS: { key: string; label: string; statuses: EnrollmentStatus[] | null }[] = [
  { key: "", label: "All", statuses: null },
  { key: "en-progreso", label: "In progress", statuses: ["IN_PROGRESS", "ASSIGNED", "OVERDUE"] },
  { key: "completados", label: "Completed", statuses: ["COMPLETED", "PASSED"] },
];

export function MyCoursesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const filterKey = searchParams.get("estado") ?? "";
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listMyEnrollments()
      .then(setEnrollments)
      .finally(() => setIsLoading(false));
  }, []);

  const activeFilter = FILTERS.find((f) => f.key === filterKey) ?? FILTERS[0];
  const visible = enrollments
    .filter((e) => e.status !== "CANCELLED")
    .filter((e) => !activeFilter.statuses || activeFilter.statuses.includes(e.status));

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">My courses</h1>
      <p className="mt-1 text-sm text-gray-500">Courses you are enrolled in</p>

      <div className="mt-4 flex gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setSearchParams(f.key ? { estado: f.key } : {})}
            className={`rounded-full px-3 py-1 text-sm font-medium ${
              activeFilter.key === f.key ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && <p className="text-sm text-gray-400">Loading...</p>}
        {!isLoading && visible.length === 0 && <p className="text-sm text-gray-400">No courses to show.</p>}
        {visible.map((enrollment) => (
          <button
            key={enrollment.id}
            onClick={() => navigate(`/mis-cursos/${enrollment.id}`)}
            className="flex flex-col items-start rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition hover:border-brand-300 hover:shadow"
          >
            {enrollment.course.cover_image_url ? (
              <img src={enrollment.course.cover_image_url} alt="" className="mb-3 h-28 w-full rounded-lg object-cover" />
            ) : (
              <div className="mb-3 flex h-28 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-gray-300">
                No cover
              </div>
            )}
            <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[enrollment.status]}`}>
              {STATUS_LABELS[enrollment.status]}
            </span>
            <h3 className="mt-2 text-sm font-semibold text-gray-900">{enrollment.course.title}</h3>
            {enrollment.is_required && <p className="mt-1 text-xs text-amber-600">Mandatory</p>}
            {enrollment.due_date && (
              <p className="mt-1 text-xs text-gray-400">
                Due date: {new Date(enrollment.due_date).toLocaleDateString("en-US")}
              </p>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
