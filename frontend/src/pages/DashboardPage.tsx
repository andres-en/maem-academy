import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { listCategories } from "../services/categories";
import { listGroups } from "../services/groups";
import { listMyEnrollments } from "../services/enrollments";
import { getReportSummary } from "../services/reports";
import { listUsers } from "../services/users";
import type { Enrollment, ReportSummary } from "../types";

interface Metrics {
  activeUsers: number;
  activeGroups: number;
  activeCategories: number;
}

const ACTIVE_STATUSES = new Set(["ASSIGNED", "IN_PROGRESS", "OVERDUE"]);

export function DashboardPage() {
  const { user } = useAuth();
  if (user?.role.name === "USER") {
    return <StudentDashboard />;
  }
  return <AdminDashboard />;
}

function AdminDashboard() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [summary, setSummary] = useState<ReportSummary | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [usersPage, groups, categories, reportSummary] = await Promise.all([
          listUsers({ status: "ACTIVE", page_size: 1 }),
          listGroups("ACTIVE"),
          listCategories("ACTIVE"),
          getReportSummary(),
        ]);
        setMetrics({
          activeUsers: usersPage.total,
          activeGroups: groups.length,
          activeCategories: categories.length,
        });
        setSummary(reportSummary);
      } catch {
        // el dashboard es informativo; si falla, simplemente no se muestran métricas
      }
    }
    load();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Hola, {user?.full_name?.split(" ")[0]}</h1>
      <p className="mt-1 text-sm text-gray-500">Platform overview</p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard label="Active users" value={metrics?.activeUsers} />
        <MetricCard label="Active groups" value={metrics?.activeGroups} />
        <MetricCard label="Active categories" value={metrics?.activeCategories} />
      </div>

      <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-4">
        <MetricCard label="Published courses" value={summary?.published_courses} />
        <MetricCard label="Courses in review" value={summary?.courses_in_review} />
        <MetricCard label="Active enrollments" value={summary ? summary.pending + summary.in_progress : undefined} />
        <MetricCard label="Overdue enrollments" value={summary?.overdue} />
      </div>
    </div>
  );
}

function StudentDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [enrollments, setEnrollments] = useState<Enrollment[] | null>(null);

  useEffect(() => {
    listMyEnrollments().then(setEnrollments).catch(() => setEnrollments([]));
  }, []);

  if (enrollments === null) {
    return <p className="text-sm text-gray-400">Loading...</p>;
  }

  const active = enrollments.filter((e) => ACTIVE_STATUSES.has(e.status));
  const continueLearning =
    active.find((e) => e.status === "IN_PROGRESS") ??
    [...active].sort((a, b) => (a.due_date && b.due_date ? a.due_date.localeCompare(b.due_date) : a.due_date ? -1 : 1))[0] ??
    active[0];

  const upcoming = active.filter((e) => e.due_date).sort((a, b) => (a.due_date! < b.due_date! ? -1 : 1));
  const required = active.filter((e) => e.is_required);
  const inProgress = enrollments.filter((e) => e.status === "IN_PROGRESS");
  const completed = enrollments.filter((e) => e.status === "COMPLETED" || e.status === "PASSED");

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Hola, {user?.full_name?.split(" ")[0]}</h1>
      <p className="mt-1 text-sm text-gray-500">Continue your training</p>

      {continueLearning ? (
        <button
          onClick={() => navigate(`/mis-cursos/${continueLearning.id}`)}
          className="mt-6 flex w-full items-center gap-4 rounded-xl border border-brand-200 bg-brand-50 p-5 text-left transition hover:border-brand-300"
        >
          {continueLearning.course.cover_image_url ? (
            <img src={continueLearning.course.cover_image_url} alt="" className="h-16 w-24 shrink-0 rounded-lg object-cover" />
          ) : (
            <div className="flex h-16 w-24 shrink-0 items-center justify-center rounded-lg bg-brand-100 text-xs text-brand-400">
              Course
            </div>
          )}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">Continue learning</p>
            <p className="mt-1 text-base font-semibold text-gray-900">{continueLearning.course.title}</p>
          </div>
        </button>
      ) : (
        <div className="mt-6 rounded-xl border border-dashed border-gray-200 bg-white p-5 text-sm text-gray-400">
          You have no courses assigned yet.
        </div>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <MetricCard label="Due soon" value={upcoming.length} />
        <MetricCard label="Mandatory" value={required.length} />
        <MetricCard label="In progress" value={inProgress.length} />
        <MetricCard label="Completed" value={completed.length} />
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value?: number }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-gray-900">{value ?? "..."}</p>
    </div>
  );
}
