import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { Modal } from "../components/ui/Modal";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";
import { listCategories } from "../services/categories";
import { createCourse, deleteCourse, listCourses } from "../services/courses";
import type { Category, Course, CourseStatus } from "../types";

const STATUS_LABELS: Record<CourseStatus, string> = {
  DRAFT: "Draft",
  IN_REVIEW: "In review",
  CHANGES_REQUESTED: "Changes requested",
  APPROVED: "Passed",
  PUBLISHED: "Published",
  ARCHIVED: "Archived",
};

const STATUS_COLORS: Record<CourseStatus, string> = {
  DRAFT: "bg-gray-100 text-gray-600",
  IN_REVIEW: "bg-amber-100 text-amber-800",
  CHANGES_REQUESTED: "bg-red-100 text-red-800",
  APPROVED: "bg-blue-100 text-blue-800",
  PUBLISHED: "bg-green-100 text-green-800",
  ARCHIVED: "bg-gray-200 text-gray-500",
};

function CourseStatusBadge({ status }: { status: CourseStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

export function CoursesListPage() {
  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const canCreate = hasRole("SUPERADMIN", "ADMIN", "INSTRUCTOR");
  const isAdmin = hasRole("SUPERADMIN", "ADMIN");

  const [courses, setCourses] = useState<Course[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [mineOnly, setMineOnly] = useState(!isAdmin);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    listCategories().then(setCategories).catch(() => undefined);
  }, []);

  async function refresh() {
    setIsLoading(true);
    try {
      const result = await listCourses({
        status: statusFilter || undefined,
        category_id: categoryFilter || undefined,
        mine: mineOnly,
        page_size: 50,
      });
      setCourses(result.items);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, categoryFilter, mineOnly]);

  async function handleDelete(e: React.MouseEvent, course: Course) {
    e.stopPropagation();
    if (!confirm(`Permanently delete the course "${course.title}"? This action cannot be undone.`)) return;
    setDeleteError(null);
    try {
      await deleteCourse(course.id);
      refresh();
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Could not delete the course.");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Courses</h1>
          <p className="mt-1 text-sm text-gray-500">Training authoring, content and review workflow</p>
        </div>
        {canCreate && <Button onClick={() => setShowCreate(true)}>New course</Button>}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <select className={`${inputClass} max-w-[10rem]`} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select className={`${inputClass} max-w-[10rem]`} value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input type="checkbox" checked={mineOnly} onChange={(e) => setMineOnly(e.target.checked)} />
          Only my courses
        </label>
      </div>

      {deleteError && <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</div>}

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && <p className="text-sm text-gray-400">Loading...</p>}
        {!isLoading && courses.length === 0 && <p className="text-sm text-gray-400">No courses to show.</p>}
        {courses.map((course) => (
          <div
            key={course.id}
            role="button"
            tabIndex={0}
            onClick={() => navigate(`/cursos/${course.id}`)}
            onKeyDown={(e) => e.key === "Enter" && navigate(`/cursos/${course.id}`)}
            className="relative flex cursor-pointer flex-col items-start rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition hover:border-brand-300 hover:shadow"
          >
            {isAdmin && course.status === "ARCHIVED" && (
              <button
                onClick={(e) => handleDelete(e, course)}
                className="absolute right-3 top-3 rounded bg-white/90 px-2 py-1 text-xs text-red-600 hover:underline"
              >
                Delete
              </button>
            )}
            {course.cover_image_url ? (
              <img src={course.cover_image_url} alt="" className="mb-3 h-32 w-full rounded-lg object-cover" />
            ) : (
              <div className="mb-3 flex h-32 w-full items-center justify-center rounded-lg bg-gray-100 text-gray-300">
                No cover
              </div>
            )}
            <CourseStatusBadge status={course.status} />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">{course.title}</h3>
            <p className="mt-1 line-clamp-2 text-xs text-gray-500">{course.description}</p>
            <p className="mt-2 text-xs text-gray-400">{course.owner.full_name}</p>
            {course.categories.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {course.categories.map((cat) => (
                  <span key={cat.id} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500">
                    {cat.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {showCreate && (
        <CreateCourseModal
          onClose={() => setShowCreate(false)}
          onCreated={(id) => navigate(`/cursos/${id}`)}
        />
      )}
    </div>
  );
}

function CreateCourseModal({ onClose, onCreated }: { onClose: () => void; onCreated: (id: string) => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const course = await createCourse({ title, description });
      onCreated(course.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create the course.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="New course" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <div>
          <label className={labelClass}>Title</label>
          <input required value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} className={inputClass} rows={3} />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create and continue"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
