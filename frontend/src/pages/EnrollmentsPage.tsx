import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { ApiError } from "../services/apiClient";
import { createAssignment, createEnrollments, listCourseEnrollments, cancelEnrollment, updateEnrollmentDueDate } from "../services/enrollments";
import { listCourses } from "../services/courses";
import { listGroups } from "../services/groups";
import { listUsers } from "../services/users";
import type { Course, Enrollment, EnrollmentStatus, Group, User } from "../types";

const STATUS_LABELS: Record<EnrollmentStatus, string> = {
  ASSIGNED: "Assigned",
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

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export function EnrollmentsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseId, setCourseId] = useState(searchParams.get("course") ?? "");
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    listCourses({ status: "PUBLISHED", page_size: 100 }).then((page) => setCourses(page.items));
  }, []);

  async function refreshRoster(id: string) {
    setIsLoading(true);
    try {
      const page = await listCourseEnrollments(id);
      setEnrollments(page.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the roster.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (courseId) {
      setSearchParams({ course: courseId });
      refreshRoster(courseId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId]);

  async function handleCancel(enrollmentId: string) {
    if (!confirm("Cancel this enrollment?")) return;
    try {
      await cancelEnrollment(enrollmentId);
      refreshRoster(courseId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not cancel the enrollment.");
    }
  }

  async function handleDueDateChange(enrollmentId: string, value: string) {
    try {
      await updateEnrollmentDueDate(enrollmentId, value ? new Date(value).toISOString() : null);
      refreshRoster(courseId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not update the due date.");
    }
  }

  const selectedCourse = courses.find((c) => c.id === courseId);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Enrollments</h1>
      <p className="mt-1 text-sm text-gray-500">Enroll users or whole groups in published courses</p>

      <div className="mt-4">
        <label className={labelClass}>Course</label>
        <select className={`${inputClass} max-w-md`} value={courseId} onChange={(e) => setCourseId(e.target.value)}>
          <option value="">Select a published course...</option>
          {courses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      {notice && <div className="mt-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{notice}</div>}

      {selectedCourse && (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <NewEnrollmentForm
              courseId={selectedCourse.id}
              onDone={(message) => {
                setNotice(message);
                setError(null);
                refreshRoster(selectedCourse.id);
              }}
              onError={(message) => {
                setError(message);
                setNotice(null);
              }}
            />
          </div>

          <div className="lg:col-span-2">
            <h2 className="mb-2 text-sm font-semibold text-gray-700">
              Matriculados en "{selectedCourse.title}" ({enrollments.length})
            </h2>
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <Th>User</Th>
                    <Th>Type</Th>
                    <Th>Status</Th>
                    <Th>Mandatory</Th>
                    <Th>Due date</Th>
                    <Th />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {isLoading && (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-gray-400">
                        Loading...
                      </td>
                    </tr>
                  )}
                  {!isLoading && enrollments.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-gray-400">
                        No enrollments yet.
                      </td>
                    </tr>
                  )}
                  {enrollments.map((e) => (
                    <tr key={e.id}>
                      <td className="px-4 py-2">
                        <p className="font-medium text-gray-800">{e.user.full_name}</p>
                        <p className="text-xs text-gray-400">{e.user.email}</p>
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500">{e.enrollment_type}</td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[e.status]}`}>
                          {STATUS_LABELS[e.status]}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500">{e.is_required ? "Yes" : "No"}</td>
                      <td className="px-4 py-2">
                        {e.status === "CANCELLED" ? (
                          <span className="text-xs text-gray-400">{formatDate(e.due_date)}</span>
                        ) : (
                          <input
                            type="date"
                            className="rounded border border-gray-200 px-1.5 py-0.5 text-xs"
                            defaultValue={e.due_date ? e.due_date.slice(0, 10) : ""}
                            onBlur={(ev) => handleDueDateChange(e.id, ev.target.value)}
                          />
                        )}
                      </td>
                      <td className="px-4 py-2 text-right">
                        {e.status !== "CANCELLED" && (
                          <button className="text-xs text-red-600 hover:underline" onClick={() => handleCancel(e.id)}>
                            Cancel
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">{children}</th>;
}

function NewEnrollmentForm({
  courseId,
  onDone,
  onError,
}: {
  courseId: string;
  onDone: (message: string) => void;
  onError: (message: string) => void;
}) {
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroupIds, setSelectedGroupIds] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState("");
  const [candidates, setCandidates] = useState<User[]>([]);
  const [selectedUserIds, setSelectedUserIds] = useState<Set<string>>(new Set());
  const [isRequired, setIsRequired] = useState(false);
  const [dueDate, setDueDate] = useState("");
  const [overdueAction, setOverdueAction] = useState<"ALLOW_CONTINUE" | "BLOCK">("ALLOW_CONTINUE");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    listGroups("ACTIVE").then(setGroups);
  }, []);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      const page = await listUsers({ search, page_size: 15, status: "ACTIVE" });
      setCandidates(page.items);
    }, 250);
    return () => clearTimeout(timeout);
  }, [search]);

  function toggleGroup(id: string) {
    setSelectedGroupIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleUser(id: string) {
    setSelectedUserIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selectedGroupIds.size === 0 && selectedUserIds.size === 0) {
      onError("Select at least one user or group.");
      return;
    }
    setIsSubmitting(true);
    try {
      const isoDueDate = dueDate ? new Date(`${dueDate}T23:59:59`).toISOString() : null;
      if (selectedGroupIds.size > 0) {
        const result = await createAssignment(courseId, {
          user_ids: Array.from(selectedUserIds),
          group_ids: Array.from(selectedGroupIds),
          is_required: isRequired,
          due_date: isoDueDate,
          overdue_action: overdueAction,
        });
        onDone(`${result.enrollments_created} enrollment(s) created, ${result.enrollments_skipped} skipped (already active).`);
      } else {
        const result = await createEnrollments(courseId, {
          user_ids: Array.from(selectedUserIds),
          is_required: isRequired,
          due_date: isoDueDate,
        });
        onDone(`${result.created} enrollment(s) created, ${result.skipped} skipped (already active).`);
      }
      setSelectedGroupIds(new Set());
      setSelectedUserIds(new Set());
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not enroll.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-gray-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-gray-700">New enrollment</h2>

      <div>
        <label className={labelClass}>Groups</label>
        <div className="max-h-28 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
          {groups.length === 0 && <p className="text-xs text-gray-400">No active groups.</p>}
          {groups.map((g) => (
            <label key={g.id} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={selectedGroupIds.has(g.id)} onChange={() => toggleGroup(g.id)} />
              {g.name} <span className="text-xs text-gray-400">({g.member_count})</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className={labelClass}>Individual users</label>
        <input className={`${inputClass} mb-2`} placeholder="Search user..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="max-h-32 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
          {candidates.map((u) => (
            <label key={u.id} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={selectedUserIds.has(u.id)} onChange={() => toggleUser(u.id)} />
              {u.full_name} <span className="text-xs text-gray-400">{u.email}</span>
            </label>
          ))}
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={isRequired} onChange={(e) => setIsRequired(e.target.checked)} />
        Mandatory course
      </label>

      <div>
        <label className={labelClass}>Due date (optional)</label>
        <input type="date" className={inputClass} value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </div>

      <div>
        <label className={labelClass}>When overdue</label>
        <select className={inputClass} value={overdueAction} onChange={(e) => setOverdueAction(e.target.value as "ALLOW_CONTINUE" | "BLOCK")}>
          <option value="ALLOW_CONTINUE">Allow to continue and mark as overdue</option>
          <option value="BLOCK">Block</option>
        </select>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Enrolling..." : "Enroll"}
      </Button>
    </form>
  );
}
