import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { Modal } from "../components/ui/Modal";
import { AssessmentSection } from "../components/courses/AssessmentBuilder";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";
import { listCategories } from "../services/categories";
import {
  addCollaborators,
  approveCourse,
  archiveCourse,
  createContent,
  createLesson,
  createModule,
  deleteContent,
  deleteCourse,
  deleteLesson,
  deleteModule,
  forceDeleteCourse,
  getCourse,
  moveContent,
  moveLesson,
  moveModule,
  publishCourse,
  removeCollaborator,
  requestChanges,
  submitForReview,
  updateCourse,
  updateLesson,
  updateModule,
  uploadCoverImage,
} from "../services/courses";
import { listUsers } from "../services/users";
import type { Category, CourseDetail, CourseModule, Lesson, LessonContent, User } from "../types";

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  IN_REVIEW: "In review",
  CHANGES_REQUESTED: "Changes requested",
  APPROVED: "Passed",
  PUBLISHED: "Published",
  ARCHIVED: "Archived",
};

const CONTENT_TYPE_LABELS: Record<string, string> = {
  TEXT: "Text",
  VIDEO: "Video",
  PDF: "PDF",
  IMAGE: "Image",
  AUDIO: "Audio",
  YOUTUBE: "YouTube",
  VIMEO: "Vimeo",
  LINK: "Link",
};

const FILE_CONTENT_TYPES = new Set(["VIDEO", "PDF", "IMAGE", "AUDIO"]);
const URL_CONTENT_TYPES = new Set(["YOUTUBE", "VIMEO", "LINK"]);

export function CourseBuilderPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();
  const isAdmin = hasRole("SUPERADMIN", "ADMIN");
  const isSuperAdmin = hasRole("SUPERADMIN");

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCollaborators, setShowCollaborators] = useState(false);
  const [showRequestChanges, setShowRequestChanges] = useState(false);
  const [showForceDelete, setShowForceDelete] = useState(false);

  const canEdit =
    !!course &&
    (isAdmin || course.owner.id === user?.id || course.collaborators.some((c) => c.id === user?.id));

  async function refresh() {
    if (!id) return;
    setIsLoading(true);
    try {
      setCourse(await getCourse(id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the course.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    listCategories().then(setCategories).catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function runAction<T>(action: () => Promise<T>) {
    setError(null);
    try {
      await action();
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function handleDeleteCourse() {
    if (!course) return;
    if (!confirm(`Permanently delete the course "${course.title}"? This action cannot be undone.`)) return;
    setError(null);
    try {
      await deleteCourse(course.id);
      navigate("/cursos");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete the course.");
    }
  }

  if (isLoading) return <p className="text-sm text-gray-400">Loading...</p>;
  if (!course) return <p className="text-sm text-red-600">{error || "Course not found."}</p>;

  return (
    <div className="pb-16">
      <button onClick={() => navigate("/cursos")} className="mb-4 text-sm text-gray-500 hover:underline">
        ← Back to courses
      </button>

      {error && <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <CourseInfoPanel
        course={course}
        categories={categories}
        canEdit={canEdit}
        onSaved={refresh}
        onError={setError}
        onManageCollaborators={() => setShowCollaborators(true)}
      />

      <ReviewPanel
        course={course}
        canEdit={canEdit}
        isAdmin={isAdmin}
        isSuperAdmin={isSuperAdmin}
        onSubmitReview={() => runAction(() => submitForReview(course.id))}
        onApprove={() => runAction(() => approveCourse(course.id))}
        onRequestChanges={() => setShowRequestChanges(true)}
        onPublish={() => runAction(() => publishCourse(course.id))}
        onArchive={() => runAction(() => archiveCourse(course.id))}
        onDelete={handleDeleteCourse}
        onForceDelete={() => setShowForceDelete(true)}
      />

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Course content</h2>
        </div>

        <div className="mt-4 space-y-4">
          {course.modules.map((module, index) => (
            <ModuleCard
              key={module.id}
              module={module}
              canEdit={canEdit}
              isFirst={index === 0}
              isLast={index === course.modules.length - 1}
              onChanged={refresh}
              onError={setError}
            />
          ))}
        </div>

        {canEdit && (
          <AddModuleForm courseId={course.id} onCreated={refresh} onError={setError} />
        )}
      </div>

      <AssessmentSection course={course} canEdit={canEdit} />

      {showCollaborators && (
        <CollaboratorsModal
          course={course}
          onClose={() => setShowCollaborators(false)}
          onChanged={refresh}
        />
      )}

      {showRequestChanges && (
        <RequestChangesModal
          onClose={() => setShowRequestChanges(false)}
          onConfirm={async (comment) => {
            await runAction(() => requestChanges(course.id, comment));
            setShowRequestChanges(false);
          }}
        />
      )}

      {showForceDelete && (
        <ForceDeleteModal
          course={course}
          onClose={() => setShowForceDelete(false)}
          onConfirm={async (confirmTitle) => {
            setError(null);
            try {
              await forceDeleteCourse(course.id, confirmTitle);
              navigate("/cursos");
            } catch (err) {
              setError(err instanceof ApiError ? err.message : "Could not force-delete the course.");
              setShowForceDelete(false);
            }
          }}
        />
      )}
    </div>
  );
}

function CourseInfoPanel({
  course,
  categories,
  canEdit,
  onSaved,
  onError,
  onManageCollaborators,
}: {
  course: CourseDetail;
  categories: Category[];
  canEdit: boolean;
  onSaved: () => void;
  onError: (message: string) => void;
  onManageCollaborators: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(course.title);
  const [description, setDescription] = useState(course.description ?? "");
  const [duration, setDuration] = useState(course.estimated_duration_minutes?.toString() ?? "");
  const [categoryIds, setCategoryIds] = useState<Set<string>>(new Set(course.categories.map((c) => c.id)));
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setTitle(course.title);
    setDescription(course.description ?? "");
    setDuration(course.estimated_duration_minutes?.toString() ?? "");
    setCategoryIds(new Set(course.categories.map((c) => c.id)));
  }, [course]);

  function toggleCategory(id: string) {
    setCategoryIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSave() {
    setIsSubmitting(true);
    try {
      await updateCourse(course.id, {
        title,
        description,
        estimated_duration_minutes: duration ? Number(duration) : null,
        category_ids: Array.from(categoryIds),
      });
      setEditing(false);
      onSaved();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not save the course.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCoverUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await uploadCoverImage(course.id, file);
      onSaved();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not upload the cover image.");
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="sm:w-48">
          {course.cover_image_url ? (
            <img src={course.cover_image_url} alt="" className="h-32 w-full rounded-lg object-cover" />
          ) : (
            <div className="flex h-32 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-gray-400">
              No cover
            </div>
          )}
          {canEdit && (
            <label className="mt-2 block cursor-pointer text-center text-xs text-brand-600 hover:underline">
              Change cover
              <input type="file" accept="image/*" className="hidden" onChange={handleCoverUpload} />
            </label>
          )}
        </div>

        <div className="flex-1">
          {!editing ? (
            <>
              <div className="flex items-start justify-between">
                <h1 className="text-xl font-semibold text-gray-900">{course.title}</h1>
                {canEdit && (
                  <button className="text-sm text-brand-600 hover:underline" onClick={() => setEditing(true)}>
                    Edit
                  </button>
                )}
              </div>
              <p className="mt-1 text-sm text-gray-500">{course.description || "No description."}</p>
              <p className="mt-2 text-xs text-gray-400">
                {course.estimated_duration_minutes ? `${course.estimated_duration_minutes} min` : "Duration not set"}
                {" · "}Owner: {course.owner.full_name}
              </p>
              {course.categories.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {course.categories.map((cat) => (
                    <span key={cat.id} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500">
                      {cat.name}
                    </span>
                  ))}
                </div>
              )}
              {canEdit && (
                <button className="mt-3 text-sm text-brand-600 hover:underline" onClick={onManageCollaborators}>
                  Collaborators ({course.collaborators.length})
                </button>
              )}
            </>
          ) : (
            <div className="space-y-3">
              <div>
                <label className={labelClass}>Title</label>
                <input value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Description</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} className={inputClass} rows={2} />
              </div>
              <div>
                <label className={labelClass}>Estimated duration (minutes)</label>
                <input
                  type="number"
                  min={0}
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  className={`${inputClass} max-w-[10rem]`}
                />
              </div>
              <div>
                <label className={labelClass}>Categories</label>
                <div className="flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <label key={cat.id} className="flex items-center gap-1 text-sm">
                      <input type="checkbox" checked={categoryIds.has(cat.id)} onChange={() => toggleCategory(cat.id)} />
                      {cat.name}
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save"}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ReviewPanel({
  course,
  canEdit,
  isAdmin,
  isSuperAdmin,
  onSubmitReview,
  onApprove,
  onRequestChanges,
  onPublish,
  onArchive,
  onDelete,
  onForceDelete,
}: {
  course: CourseDetail;
  canEdit: boolean;
  isAdmin: boolean;
  isSuperAdmin: boolean;
  onSubmitReview: () => void;
  onApprove: () => void;
  onRequestChanges: () => void;
  onPublish: () => void;
  onArchive: () => void;
  onDelete: () => void;
  onForceDelete: () => void;
}) {
  const status = course.status;
  return (
    <div className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-gray-200 bg-white p-4">
      <span className="text-sm font-medium text-gray-700">Status: {STATUS_LABELS[status]}</span>
      {status === "CHANGES_REQUESTED" && course.review_comment && (
        <span className="rounded bg-red-50 px-2 py-1 text-xs text-red-700">
          Reviewer comment: {course.review_comment}
        </span>
      )}
      <div className="ml-auto flex gap-2">
        {canEdit && (status === "DRAFT" || status === "CHANGES_REQUESTED") && (
          <Button onClick={onSubmitReview}>Submit for review</Button>
        )}
        {isAdmin && status === "IN_REVIEW" && (
          <>
            <Button variant="secondary" onClick={onRequestChanges}>
              Request changes
            </Button>
            <Button onClick={onApprove}>Approve</Button>
          </>
        )}
        {isAdmin && status === "APPROVED" && <Button onClick={onPublish}>Publish</Button>}
        {isAdmin && status !== "ARCHIVED" && (
          <Button variant="danger" onClick={onArchive}>
            Archivar
          </Button>
        )}
        {isAdmin && status === "ARCHIVED" && (
          <Button variant="danger" onClick={onDelete}>
            Delete course
          </Button>
        )}
        {isSuperAdmin && status === "ARCHIVED" && (
          <button onClick={onForceDelete} className="text-xs text-red-400 hover:text-red-600 hover:underline">
            Force delete (removes enrollments and results)
          </button>
        )}
        {isAdmin && status === "PUBLISHED" && (
          <Link to={`/matriculas?course=${course.id}`} className="text-sm text-brand-600 hover:underline">
            Manage enrollments →
          </Link>
        )}
      </div>
    </div>
  );
}

function RequestChangesModal({ onClose, onConfirm }: { onClose: () => void; onConfirm: (comment: string) => void }) {
  const [comment, setComment] = useState("");
  return (
    <Modal title="Request changes" onClose={onClose}>
      <div className="space-y-3">
        <label className={labelClass}>Comment for the instructor</label>
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} className={inputClass} rows={4} />
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button disabled={!comment.trim()} onClick={() => onConfirm(comment)}>
            Enviar
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function CollaboratorsModal({
  course,
  onClose,
  onChanged,
}: {
  course: CourseDetail;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [search, setSearch] = useState("");
  const [candidates, setCandidates] = useState<User[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      const page = await listUsers({ search, page_size: 20, status: "ACTIVE" });
      setCandidates(page.items);
    }, 250);
    return () => clearTimeout(timeout);
  }, [search]);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleAdd() {
    setError(null);
    try {
      await addCollaborators(course.id, Array.from(selected));
      setSelected(new Set());
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add the collaborators.");
    }
  }

  async function handleRemove(userId: string) {
    setError(null);
    try {
      await removeCollaborator(course.id, userId);
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not remove the collaborator.");
    }
  }

  const collaboratorIds = new Set(course.collaborators.map((c) => c.id));

  return (
    <Modal title="Course collaborators" onClose={onClose} widthClass="max-w-2xl">
      {error && <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Current collaborators ({course.collaborators.length})</h3>
          <ul className="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
            {course.collaborators.length === 0 && <li className="px-2 py-1 text-sm text-gray-400">No collaborators.</li>}
            {course.collaborators.map((collab) => (
              <li key={collab.id} className="flex items-center justify-between rounded-md px-2 py-1 text-sm hover:bg-gray-50">
                <span>
                  {collab.full_name}
                  <span className="ml-1 text-xs text-gray-400">{collab.email}</span>
                </span>
                <button onClick={() => handleRemove(collab.id)} className="text-xs text-red-600 hover:underline">
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Add collaborators</h3>
          <input className={`${inputClass} mb-2`} placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <ul className="max-h-48 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
            {candidates
              .filter((u) => !collaboratorIds.has(u.id) && u.id !== course.owner.id)
              .map((candidate) => (
                <li key={candidate.id} className="flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-gray-50">
                  <input type="checkbox" checked={selected.has(candidate.id)} onChange={() => toggle(candidate.id)} />
                  <span>
                    {candidate.full_name}
                    <span className="ml-1 text-xs text-gray-400">{candidate.email}</span>
                  </span>
                </li>
              ))}
          </ul>
          <Button className="mt-2 w-full" disabled={selected.size === 0} onClick={handleAdd}>
            Add {selected.size > 0 ? `(${selected.size})` : ""}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function AddModuleForm({ courseId, onCreated, onError }: { courseId: string; onCreated: () => void; onError: (m: string) => void }) {
  const [title, setTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setIsSubmitting(true);
    try {
      await createModule(courseId, { title });
      setTitle("");
      onCreated();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not create the module.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
      <input
        className={inputClass}
        placeholder="New module title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Button type="submit" disabled={isSubmitting || !title.trim()}>
        Add module
      </Button>
    </form>
  );
}

function ModuleCard({
  module,
  canEdit,
  isFirst,
  isLast,
  onChanged,
  onError,
}: {
  module: CourseModule;
  canEdit: boolean;
  isFirst: boolean;
  isLast: boolean;
  onChanged: () => void;
  onError: (m: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(module.title);
  const [description, setDescription] = useState(module.description ?? "");

  async function handleSave() {
    try {
      await updateModule(module.id, { title, description });
      setEditing(false);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not update the module.");
    }
  }

  async function handleDelete() {
    if (!confirm(`Delete the module "${module.title}" and all its content?`)) return;
    try {
      await deleteModule(module.id);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not delete the module.");
    }
  }

  async function handleMove(direction: "up" | "down") {
    try {
      await moveModule(module.id, direction);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not move the module.");
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between">
        {!editing ? (
          <div>
            <h3 className="text-sm font-semibold text-gray-900">{module.title}</h3>
            {module.description && <p className="text-xs text-gray-500">{module.description}</p>}
          </div>
        ) : (
          <div className="flex-1 space-y-2">
            <input className={inputClass} value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea className={inputClass} rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave}>Save</Button>
            </div>
          </div>
        )}
        {canEdit && !editing && (
          <div className="flex items-center gap-2 text-xs">
            <button disabled={isFirst} onClick={() => handleMove("up")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
              ▲
            </button>
            <button disabled={isLast} onClick={() => handleMove("down")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
              ▼
            </button>
            <button onClick={() => setEditing(true)} className="text-brand-600 hover:underline">
              Edit
            </button>
            <button onClick={handleDelete} className="text-red-600 hover:underline">
              Delete
            </button>
          </div>
        )}
      </div>

      <div className="mt-3 space-y-2 border-t border-gray-100 pt-3">
        {module.lessons.map((lesson, index) => (
          <LessonCard
            key={lesson.id}
            lesson={lesson}
            canEdit={canEdit}
            isFirst={index === 0}
            isLast={index === module.lessons.length - 1}
            onChanged={onChanged}
            onError={onError}
          />
        ))}
        {canEdit && <AddLessonForm moduleId={module.id} onCreated={onChanged} onError={onError} />}
      </div>
    </div>
  );
}

function AddLessonForm({ moduleId, onCreated, onError }: { moduleId: string; onCreated: () => void; onError: (m: string) => void }) {
  const [title, setTitle] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await createLesson(moduleId, { title, completion_type: "MANUAL" });
      setTitle("");
      onCreated();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not create the lesson.");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 pl-4">
      <input className={`${inputClass} text-sm`} placeholder="New lesson title..." value={title} onChange={(e) => setTitle(e.target.value)} />
      <Button type="submit" variant="secondary" disabled={!title.trim()}>
        Add lesson
      </Button>
    </form>
  );
}

function LessonCard({
  lesson,
  canEdit,
  isFirst,
  isLast,
  onChanged,
  onError,
}: {
  lesson: Lesson;
  canEdit: boolean;
  isFirst: boolean;
  isLast: boolean;
  onChanged: () => void;
  onError: (m: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(lesson.title);
  const [completionType, setCompletionType] = useState(lesson.completion_type);
  const [showAddContent, setShowAddContent] = useState(false);

  async function handleSave() {
    try {
      await updateLesson(lesson.id, { title, completion_type: completionType });
      setEditing(false);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not update the lesson.");
    }
  }

  async function handleDelete() {
    if (!confirm(`Delete the lesson "${lesson.title}"?`)) return;
    try {
      await deleteLesson(lesson.id);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not delete the lesson.");
    }
  }

  async function handleMove(direction: "up" | "down") {
    try {
      await moveLesson(lesson.id, direction);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not move the lesson.");
    }
  }

  return (
    <div className="rounded-lg bg-gray-50 p-3 pl-4">
      <div className="flex items-start justify-between">
        {!editing ? (
          <div>
            <p className="text-sm font-medium text-gray-800">{lesson.title}</p>
            <p className="text-xs text-gray-400">
              Completion: {lesson.completion_type === "MANUAL" ? "Manual" : "Automatic"}
            </p>
          </div>
        ) : (
          <div className="flex-1 space-y-2">
            <input className={`${inputClass} text-sm`} value={title} onChange={(e) => setTitle(e.target.value)} />
            <select
              className={`${inputClass} text-sm`}
              value={completionType}
              onChange={(e) => setCompletionType(e.target.value as "MANUAL" | "AUTO")}
            >
              <option value="MANUAL">Manual</option>
              <option value="AUTO">Automatic</option>
            </select>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave}>Save</Button>
            </div>
          </div>
        )}
        {canEdit && !editing && (
          <div className="flex items-center gap-2 text-xs">
            <button disabled={isFirst} onClick={() => handleMove("up")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
              ▲
            </button>
            <button disabled={isLast} onClick={() => handleMove("down")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
              ▼
            </button>
            <button onClick={() => setEditing(true)} className="text-brand-600 hover:underline">
              Edit
            </button>
            <button onClick={handleDelete} className="text-red-600 hover:underline">
              Delete
            </button>
          </div>
        )}
      </div>

      <div className="mt-2 space-y-2">
        {lesson.contents.map((content, index) => (
          <ContentItem
            key={content.id}
            content={content}
            canEdit={canEdit}
            isFirst={index === 0}
            isLast={index === lesson.contents.length - 1}
            onChanged={onChanged}
            onError={onError}
          />
        ))}
        {canEdit && (
          <button className="text-xs text-brand-600 hover:underline" onClick={() => setShowAddContent(true)}>
            + Add content
          </button>
        )}
      </div>

      {showAddContent && (
        <AddContentModal lessonId={lesson.id} onClose={() => setShowAddContent(false)} onCreated={onChanged} />
      )}
    </div>
  );
}

function ContentItem({
  content,
  canEdit,
  isFirst,
  isLast,
  onChanged,
  onError,
}: {
  content: LessonContent;
  canEdit: boolean;
  isFirst: boolean;
  isLast: boolean;
  onChanged: () => void;
  onError: (m: string) => void;
}) {
  async function handleDelete() {
    if (!confirm("Delete this content?")) return;
    try {
      await deleteContent(content.id);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not delete the content.");
    }
  }

  async function handleMove(direction: "up" | "down") {
    try {
      await moveContent(content.id, direction);
      onChanged();
    } catch (err) {
      onError(err instanceof ApiError ? err.message : "Could not move the content.");
    }
  }

  return (
    <div className="flex items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-xs">
      <div className="flex items-center gap-2 overflow-hidden">
        <span className="shrink-0 rounded bg-gray-100 px-1.5 py-0.5 font-medium text-gray-500">
          {CONTENT_TYPE_LABELS[content.content_type]}
        </span>
        <span className="truncate text-gray-700">{content.title || "(untitled)"}</span>
        <ContentPreview content={content} />
      </div>
      {canEdit && (
        <div className="flex shrink-0 items-center gap-2">
          <button disabled={isFirst} onClick={() => handleMove("up")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
            ▲
          </button>
          <button disabled={isLast} onClick={() => handleMove("down")} className="text-gray-400 hover:text-gray-700 disabled:opacity-30">
            ▼
          </button>
          <button onClick={handleDelete} className="text-red-600 hover:underline">
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

function ContentPreview({ content }: { content: LessonContent }) {
  if (content.content_type === "IMAGE" && content.file_url) {
    return <img src={content.file_url} alt="" className="h-8 w-8 rounded object-cover" />;
  }
  if ((content.content_type === "VIDEO" || content.content_type === "AUDIO" || content.content_type === "PDF") && content.file_url) {
    return (
      <a href={content.file_url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">
        View file
      </a>
    );
  }
  if (URL_CONTENT_TYPES.has(content.content_type) && content.external_url) {
    return (
      <a href={content.external_url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">
        Open link
      </a>
    );
  }
  return null;
}

function AddContentModal({ lessonId, onClose, onCreated }: { lessonId: string; onClose: () => void; onCreated: () => void }) {
  const [contentType, setContentType] = useState("TEXT");
  const [title, setTitle] = useState("");
  const [textContent, setTextContent] = useState("");
  const [externalUrl, setExternalUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await createContent(lessonId, {
        content_type: contentType,
        title: title || undefined,
        text_content: contentType === "TEXT" ? textContent : undefined,
        external_url: URL_CONTENT_TYPES.has(contentType) ? externalUrl : undefined,
        file: FILE_CONTENT_TYPES.has(contentType) && file ? file : undefined,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add the content.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="Add content" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-3">
        {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <div>
          <label className={labelClass}>Content type</label>
          <select className={inputClass} value={contentType} onChange={(e) => setContentType(e.target.value)}>
            {Object.entries(CONTENT_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Title (optional)</label>
          <input className={inputClass} value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>

        {contentType === "TEXT" && (
          <div>
            <label className={labelClass}>Text</label>
            <textarea required className={inputClass} rows={4} value={textContent} onChange={(e) => setTextContent(e.target.value)} />
          </div>
        )}

        {URL_CONTENT_TYPES.has(contentType) && (
          <div>
            <label className={labelClass}>URL</label>
            <input
              required
              type="url"
              className={inputClass}
              placeholder="https://..."
              value={externalUrl}
              onChange={(e) => setExternalUrl(e.target.value)}
            />
          </div>
        )}

        {FILE_CONTENT_TYPES.has(contentType) && (
          <div>
            <label className={labelClass}>File</label>
            <input required type="file" className={inputClass} onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Uploading..." : "Add"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function ForceDeleteModal({
  course,
  onClose,
  onConfirm,
}: {
  course: CourseDetail;
  onClose: () => void;
  onConfirm: (confirmTitle: string) => Promise<void>;
}) {
  const [confirmTitle, setConfirmTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const matches = confirmTitle === course.title;

  async function handleConfirm() {
    setIsSubmitting(true);
    try {
      await onConfirm(confirmTitle);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="Force-delete course" onClose={onClose}>
      <div className="space-y-4">
        <div className="rounded-lg bg-red-50 px-3 py-3 text-sm text-red-700">
          <p className="font-semibold">This action cannot be undone.</p>
          <p className="mt-1">
            The course <strong>"{course.title}"</strong> will be deleted together with{" "}
            <strong>all enrollments, progress and assessment results</strong> of every enrolled
            student — including courses already passed. This information cannot be recovered afterwards.
          </p>
        </div>
        <div>
          <label className={labelClass}>
            Type the exact course title (<span className="font-mono">{course.title}</span>) to confirm
          </label>
          <input
            className={inputClass}
            value={confirmTitle}
            onChange={(e) => setConfirmTitle(e.target.value)}
            autoFocus
          />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" variant="danger" disabled={!matches || isSubmitting} onClick={handleConfirm}>
            {isSubmitting ? "Deleting..." : "Force permanent deletion"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
