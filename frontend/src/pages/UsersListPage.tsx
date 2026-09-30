import { useEffect, useState } from "react";
import { StatusBadge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Modal } from "../components/ui/Modal";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";
import { listGroups } from "../services/groups";
import { listRoles } from "../services/roles";
import {
  confirmImport,
  createUser,
  deleteUser,
  downloadImportTemplate,
  forceDeleteUser,
  getUser,
  listUsers,
  setUserStatus,
  updateUser,
  validateImport,
} from "../services/users";
import type { Group, ImportConfirmResponse, ImportPreviewResponse, Role, User, UserDetail } from "../types";

const PAGE_SIZE = 15;

export function UsersListPage() {
  const { hasRole } = useAuth();
  const canManage = hasRole("SUPERADMIN", "ADMIN");
  const isSuperAdmin = hasRole("SUPERADMIN");

  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [groupFilter, setGroupFilter] = useState("");
  const [roles, setRoles] = useState<Role[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingUserId, setEditingUserId] = useState<string | "new" | null>(null);
  const [showImport, setShowImport] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [forceDeleteTarget, setForceDeleteTarget] = useState<User | null>(null);

  useEffect(() => {
    listRoles().then(setRoles).catch(() => undefined);
    listGroups().then(setGroups).catch(() => undefined);
  }, []);

  async function refresh() {
    setIsLoading(true);
    try {
      const result = await listUsers({
        page,
        page_size: PAGE_SIZE,
        search: search || undefined,
        role_id: roleFilter || undefined,
        status: statusFilter || undefined,
        group_id: groupFilter || undefined,
      });
      setUsers(result.items);
      setTotal(result.total);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, roleFilter, statusFilter, groupFilter]);

  async function toggleStatus(user: User) {
    const newStatus = user.status === "ACTIVE" ? "INACTIVE" : "ACTIVE";
    await setUserStatus(user.id, newStatus);
    refresh();
  }

  async function handleDelete(user: User) {
    if (!confirm(`Permanently delete "${user.full_name}"? This action cannot be undone.`)) return;
    setDeleteError(null);
    try {
      await deleteUser(user.id);
      refresh();
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Could not delete the user.");
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Users</h1>
          <p className="mt-1 text-sm text-gray-500">{total} usuario(s) registrados</p>
        </div>
        {canManage && (
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setShowImport(true)}>
              Bulk upload
            </Button>
            <Button onClick={() => setEditingUserId("new")}>New user</Button>
          </div>
        )}
      </div>

      {deleteError && <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</div>}

      <div className="mt-4 flex flex-wrap gap-2">
        <input
          className={`${inputClass} max-w-xs`}
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
        />
        <select
          className={`${inputClass} max-w-[10rem]`}
          value={roleFilter}
          onChange={(e) => {
            setPage(1);
            setRoleFilter(e.target.value);
          }}
        >
          <option value="">All roles</option>
          {roles.map((r) => (
            <option key={r.id} value={r.id}>
              {r.display_name}
            </option>
          ))}
        </select>
        <select
          className={`${inputClass} max-w-[10rem]`}
          value={groupFilter}
          onChange={(e) => {
            setPage(1);
            setGroupFilter(e.target.value);
          }}
        >
          <option value="">All groups</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
        <select
          className={`${inputClass} max-w-[10rem]`}
          value={statusFilter}
          onChange={(e) => {
            setPage(1);
            setStatusFilter(e.target.value);
          }}
        >
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Role</Th>
              <Th>Status</Th>
              {canManage && <Th />}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-400">
                  Loading...
                </td>
              </tr>
            )}
            {!isLoading && users.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-400">
                  No users found.
                </td>
              </tr>
            )}
            {users.map((user) => (
              <tr key={user.id}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{user.full_name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{user.email}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{user.role.display_name}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={user.status} />
                </td>
                {canManage && (
                  <td className="px-4 py-3 text-right text-sm">
                    <button className="mr-3 text-brand-600 hover:underline" onClick={() => setEditingUserId(user.id)}>
                      Edit
                    </button>
                    <button className="mr-3 text-gray-500 hover:underline" onClick={() => toggleStatus(user)}>
                      {user.status === "ACTIVE" ? "Deactivate" : "Activate"}
                    </button>
                    {user.status === "INACTIVE" && (
                      <button className="mr-3 text-red-600 hover:underline" onClick={() => handleDelete(user)}>
                        Delete
                      </button>
                    )}
                    {isSuperAdmin && user.status === "INACTIVE" && (
                      <button className="text-xs text-red-400 hover:text-red-600 hover:underline" onClick={() => setForceDeleteTarget(user)}>
                        Forzar
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
        <span>
          Page {page} of {totalPages}
        </span>
        <div className="flex gap-2">
          <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </Button>
          <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Next
          </Button>
        </div>
      </div>

      {editingUserId && (
        <UserFormModal
          userId={editingUserId === "new" ? null : editingUserId}
          roles={roles}
          groups={groups}
          onClose={() => setEditingUserId(null)}
          onSaved={() => {
            setEditingUserId(null);
            refresh();
          }}
        />
      )}

      {showImport && (
        <ImportWizardModal
          onClose={() => {
            setShowImport(false);
            refresh();
          }}
        />
      )}

      {forceDeleteTarget && (
        <ForceDeleteUserModal
          user={forceDeleteTarget}
          onClose={() => setForceDeleteTarget(null)}
          onConfirm={async (confirmEmail) => {
            setDeleteError(null);
            try {
              await forceDeleteUser(forceDeleteTarget.id, confirmEmail);
              setForceDeleteTarget(null);
              refresh();
            } catch (err) {
              setDeleteError(err instanceof ApiError ? err.message : "Could not force-delete the user.");
              setForceDeleteTarget(null);
            }
          }}
        />
      )}
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">{children}</th>;
}

function UserFormModal({
  userId,
  roles,
  groups,
  onClose,
  onSaved,
}: {
  userId: string | null;
  roles: Role[];
  groups: Group[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const [detail, setDetail] = useState<UserDetail | null>(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [roleId, setRoleId] = useState("");
  const [groupIds, setGroupIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(!!userId);

  useEffect(() => {
    if (!userId) return;
    getUser(userId).then((u) => {
      setDetail(u);
      setFullName(u.full_name);
      setEmail(u.email);
      setRoleId(u.role.id);
      setGroupIds(new Set(u.groups.map((g) => g.id)));
      setIsLoading(false);
    });
  }, [userId]);

  function toggleGroup(id: string) {
    setGroupIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (userId) {
        await updateUser(userId, { full_name: fullName, role_id: roleId, group_ids: Array.from(groupIds) });
      } else {
        await createUser({ full_name: fullName, email, role_id: roleId, group_ids: Array.from(groupIds) });
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save the user.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title={userId ? "Edit user" : "New user"} onClose={onClose}>
      {isLoading ? (
        <p className="text-sm text-gray-400">Loading...</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
          <div>
            <label className={labelClass}>Full name</label>
            <input required value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Email</label>
            <input
              required
              type="email"
              disabled={!!userId}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`${inputClass} ${userId ? "bg-gray-100 text-gray-500" : ""}`}
            />
            {userId && <p className="mt-1 text-xs text-gray-400">The email cannot be changed.</p>}
          </div>
          <div>
            <label className={labelClass}>Role</label>
            <select required value={roleId} onChange={(e) => setRoleId(e.target.value)} className={inputClass}>
              <option value="" disabled>
                Select a role
              </option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.display_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Groups</label>
            <div className="max-h-32 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
              {groups.length === 0 && <p className="text-xs text-gray-400">No groups created.</p>}
              {groups.map((g) => (
                <label key={g.id} className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={groupIds.has(g.id)} onChange={() => toggleGroup(g.id)} />
                  {g.name}
                </label>
              ))}
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || !roleId}>
              {isSubmitting ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}

type ImportStep = "upload" | "preview" | "done";

function ImportWizardModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState<ImportStep>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [result, setResult] = useState<ImportConfirmResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function handleDownloadTemplate() {
    const blob = await downloadImportTemplate();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "plantilla_usuarios.xlsx";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleValidate() {
    if (!file) return;
    setError(null);
    setIsBusy(true);
    try {
      const response = await validateImport(file);
      setPreview(response);
      setStep("preview");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not validate the file.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleConfirm() {
    if (!file) return;
    setError(null);
    setIsBusy(true);
    try {
      const response = await confirmImport(file);
      setResult(response);
      setStep("done");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not confirm the import.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <Modal title="Bulk user upload" onClose={onClose} widthClass="max-w-2xl">
      {error && <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      {step === "upload" && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            1. Download the template, fill it in and upload it to validate the data before the users are created.
          </p>
          <Button variant="secondary" onClick={handleDownloadTemplate}>
            Download template
          </Button>
          <div>
            <label className={labelClass}>Excel file (.xlsx)</label>
            <input
              type="file"
              accept=".xlsx"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className={inputClass}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button disabled={!file || isBusy} onClick={handleValidate}>
              {isBusy ? "Validating..." : "Validate file"}
            </Button>
          </div>
        </div>
      )}

      {step === "preview" && preview && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            {preview.total_rows} row(s): <span className="text-green-700">{preview.valid_rows} valid</span>,{" "}
            <span className="text-red-700">{preview.invalid_rows} with errors</span>.
          </p>
          <ImportRowsTable rows={preview.rows} />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setStep("upload")}>
              Back
            </Button>
            <Button disabled={preview.valid_rows === 0 || isBusy} onClick={handleConfirm}>
              {isBusy ? "Creating..." : `Create ${preview.valid_rows} valid user(s)`}
            </Button>
          </div>
        </div>
      )}

      {step === "done" && result && (
        <div className="space-y-4">
          <p className="text-sm text-gray-700">
            <span className="font-semibold text-green-700">{result.created}</span> user(s) created.{" "}
            <span className="font-semibold text-red-700">{result.skipped}</span> row(s) with errors were skipped.
          </p>
          <ImportRowsTable rows={result.rows} />
          <div className="flex justify-end">
            <Button onClick={onClose}>Close</Button>
          </div>
        </div>
      )}
    </Modal>
  );
}

function ImportRowsTable({ rows }: { rows: ImportPreviewResponse["rows"] }) {
  return (
    <div className="max-h-64 overflow-y-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left">Row</th>
            <th className="px-3 py-2 text-left">Name</th>
            <th className="px-3 py-2 text-left">Email</th>
            <th className="px-3 py-2 text-left">Errors</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row) => (
            <tr key={row.row_number} className={row.errors.length ? "bg-red-50" : ""}>
              <td className="px-3 py-2">{row.row_number}</td>
              <td className="px-3 py-2">{row.full_name || "—"}</td>
              <td className="px-3 py-2">{row.email || "—"}</td>
              <td className="px-3 py-2 text-red-700">{row.errors.join(" ") || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ForceDeleteUserModal({
  user,
  onClose,
  onConfirm,
}: {
  user: User;
  onClose: () => void;
  onConfirm: (confirmEmail: string) => Promise<void>;
}) {
  const [confirmEmail, setConfirmEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const matches = confirmEmail === user.email;

  async function handleConfirm() {
    setIsSubmitting(true);
    try {
      await onConfirm(confirmEmail);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="Force-delete user" onClose={onClose}>
      <div className="space-y-4">
        <div className="rounded-lg bg-red-50 px-3 py-3 text-sm text-red-700">
          <p className="font-semibold">This action cannot be undone.</p>
          <p className="mt-1">
            <strong>"{user.full_name}"</strong> will be deleted together with{" "}
            <strong>all of their enrollments, progress and assessment results</strong> — including courses
            already passed. If the user owns any course, the deletion stays blocked so other students are not
            affected.
          </p>
        </div>
        <div>
          <label className={labelClass}>
            Type the exact email (<span className="font-mono">{user.email}</span>) to confirm
          </label>
          <input className={inputClass} value={confirmEmail} onChange={(e) => setConfirmEmail(e.target.value)} autoFocus />
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
