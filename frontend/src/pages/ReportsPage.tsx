import { useEffect, useState } from "react";
import { AssessmentSummaryTab } from "../components/reports/AssessmentSummaryTab";
import { AttemptsDetailModal } from "../components/reports/AttemptsDetailModal";
import { inputClass } from "../components/ui/formStyles";
import { listCourses } from "../services/courses";
import { getCourseReport, getReportSummary, getUserReport } from "../services/reports";
import { listUsers } from "../services/users";
import type { Course, CourseReportRow, EnrollmentStatus, ReportSummary, User, UserReportRow } from "../types";

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

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export function ReportsPage() {
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [tab, setTab] = useState<"course" | "user" | "assessments">("course");
  const [detailEnrollmentId, setDetailEnrollmentId] = useState<string | null>(null);

  useEffect(() => {
    getReportSummary().then(setSummary);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Reports</h1>
      <p className="mt-1 text-sm text-gray-500">Overall indicators and details by course or by user</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
        <SummaryCard label="Enrolled" value={summary?.enrollments_total} />
        <SummaryCard label="Pending" value={summary?.pending} />
        <SummaryCard label="In progress" value={summary?.in_progress} />
        <SummaryCard label="Completed" value={summary?.completed} />
        <SummaryCard label="Passed" value={summary?.passed} />
        <SummaryCard label="Failed" value={summary?.failed} />
        <SummaryCard label="Overdue" value={summary?.overdue} />
        <SummaryCard label="Cancelled" value={summary?.cancelled} />
      </div>

      <div className="mt-8 flex gap-2 border-b border-gray-200">
        <TabButton active={tab === "course"} onClick={() => setTab("course")}>
          Report by course
        </TabButton>
        <TabButton active={tab === "user"} onClick={() => setTab("user")}>
          Report by user
        </TabButton>
        <TabButton active={tab === "assessments"} onClick={() => setTab("assessments")}>
          Assessment summary
        </TabButton>
      </div>

      <div className="mt-4">
        {tab === "course" && <CourseReportTab onViewAnswers={setDetailEnrollmentId} />}
        {tab === "user" && <UserReportTab onViewAnswers={setDetailEnrollmentId} />}
        {tab === "assessments" && <AssessmentSummaryTab />}
      </div>

      {detailEnrollmentId && (
        <AttemptsDetailModal enrollmentId={detailEnrollmentId} onClose={() => setDetailEnrollmentId(null)} />
      )}
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value?: number }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-3 shadow-sm">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-gray-900">{value ?? "..."}</p>
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`border-b-2 px-3 py-2 text-sm font-medium ${
        active ? "border-brand-600 text-brand-700" : "border-transparent text-gray-500 hover:text-gray-700"
      }`}
    >
      {children}
    </button>
  );
}

function ReportTable({ rows, firstColumnLabel, firstColumn, onViewAnswers }: {
  rows: (CourseReportRow | UserReportRow)[];
  firstColumnLabel: string;
  firstColumn: (row: CourseReportRow | UserReportRow) => React.ReactNode;
  onViewAnswers: (enrollmentId: string) => void;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <Th>{firstColumnLabel}</Th>
            <Th>Status</Th>
            <Th>Progress</Th>
            <Th>Score</Th>
            <Th>Enrollment date</Th>
            <Th>Completion date</Th>
            <Th>Assessments</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.length === 0 && (
            <tr>
              <td colSpan={7} className="px-4 py-6 text-center text-gray-400">
                No data to show.
              </td>
            </tr>
          )}
          {rows.map((row) => (
            <tr key={row.enrollment_id}>
              <td className="px-4 py-2">{firstColumn(row)}</td>
              <td className="px-4 py-2">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[row.status]}`}>
                  {STATUS_LABELS[row.status]}
                </span>
              </td>
              <td className="px-4 py-2 text-gray-600">{row.progress_percentage}%</td>
              <td className="px-4 py-2 text-gray-600">{row.score !== null ? `${row.score}%` : "—"}</td>
              <td className="px-4 py-2 text-xs text-gray-400">{formatDate(row.assigned_at)}</td>
              <td className="px-4 py-2 text-xs text-gray-400">{formatDate(row.completed_at)}</td>
              <td className="px-4 py-2">
                <button
                  onClick={() => onViewAnswers(row.enrollment_id)}
                  className="text-xs font-medium text-brand-700 hover:underline"
                >
                  View answers
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">{children}</th>;
}

function CourseReportTab({ onViewAnswers }: { onViewAnswers: (enrollmentId: string) => void }) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseId, setCourseId] = useState("");
  const [rows, setRows] = useState<CourseReportRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    listCourses({ page_size: 100 }).then((page) => setCourses(page.items));
  }, []);

  useEffect(() => {
    if (!courseId) {
      setRows([]);
      return;
    }
    setIsLoading(true);
    getCourseReport(courseId)
      .then(setRows)
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
      {!isLoading && courseId && (
        <ReportTable rows={rows} firstColumnLabel="User" onViewAnswers={onViewAnswers} firstColumn={(r) => {
          const row = r as CourseReportRow;
          return (
            <>
              <p className="font-medium text-gray-800">{row.user.full_name}</p>
              <p className="text-xs text-gray-400">{row.user.email}</p>
            </>
          );
        }} />
      )}
    </div>
  );
}

function UserReportTab({ onViewAnswers }: { onViewAnswers: (enrollmentId: string) => void }) {
  const [search, setSearch] = useState("");
  const [candidates, setCandidates] = useState<User[]>([]);
  const [userId, setUserId] = useState("");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [rows, setRows] = useState<UserReportRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      const page = await listUsers({ search, page_size: 15 });
      setCandidates(page.items);
    }, 250);
    return () => clearTimeout(timeout);
  }, [search]);

  useEffect(() => {
    if (!userId) {
      setRows([]);
      return;
    }
    setIsLoading(true);
    getUserReport(userId)
      .then(setRows)
      .finally(() => setIsLoading(false));
  }, [userId]);

  return (
    <div>
      <div className="mb-4 max-w-md">
        <input
          className={inputClass}
          placeholder="Search user by name or email..."
          value={selectedUser ? selectedUser.full_name : search}
          onChange={(e) => {
            setSelectedUser(null);
            setUserId("");
            setSearch(e.target.value);
          }}
        />
        {!selectedUser && search && (
          <div className="mt-1 max-h-40 overflow-y-auto rounded-lg border border-gray-200 bg-white">
            {candidates.map((u) => (
              <button
                key={u.id}
                className="block w-full px-3 py-1.5 text-left text-sm hover:bg-gray-50"
                onClick={() => {
                  setSelectedUser(u);
                  setUserId(u.id);
                  setSearch("");
                }}
              >
                {u.full_name} <span className="text-xs text-gray-400">{u.email}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      {isLoading && <p className="text-sm text-gray-400">Loading...</p>}
      {!isLoading && userId && (
        <ReportTable rows={rows} firstColumnLabel="Course" onViewAnswers={onViewAnswers} firstColumn={(r) => {
          const row = r as UserReportRow;
          return <p className="font-medium text-gray-800">{row.course.title}</p>;
        }} />
      )}
    </div>
  );
}
