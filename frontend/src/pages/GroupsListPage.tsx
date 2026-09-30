import { useEffect, useState } from "react";
import { StatusBadge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Modal } from "../components/ui/Modal";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";
import { addGroupUsers, createGroup, deleteGroup, getGroup, listGroups, removeGroupUser, setGroupStatus, updateGroup } from "../services/groups";
import { listUsers } from "../services/users";
import type { Group, GroupDetail, User } from "../types";

export function GroupsListPage() {
  const { hasRole } = useAuth();
  const canManage = hasRole("SUPERADMIN", "ADMIN");
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editing, setEditing] = useState<Group | "new" | null>(null);
  const [managingMembersOf, setManagingMembersOf] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function refresh() {
    setIsLoading(true);
    try {
      setGroups(await listGroups());
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function toggleStatus(group: Group) {
    const newStatus = group.status === "ACTIVE" ? "INACTIVE" : "ACTIVE";
    await setGroupStatus(group.id, newStatus);
    refresh();
  }

  async function handleDelete(group: Group) {
    if (!confirm(`Permanently delete the group "${group.name}"? This action cannot be undone.`)) return;
    setDeleteError(null);
    try {
      await deleteGroup(group.id);
      refresh();
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Could not delete the group.");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Groups</h1>
          <p className="mt-1 text-sm text-gray-500">Teams to organize users and bulk enrollments</p>
        </div>
        {canManage && <Button onClick={() => setEditing("new")}>New group</Button>}
      </div>

      {deleteError && <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</div>}

      <div className="mt-6 overflow-hidden rounded-xl border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <Th>Name</Th>
              <Th>Description</Th>
              <Th>Members</Th>
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
            {!isLoading && groups.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-400">
                  No groups yet.
                </td>
              </tr>
            )}
            {groups.map((group) => (
              <tr key={group.id}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{group.name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{group.description || "—"}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{group.member_count}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={group.status} />
                </td>
                {canManage && (
                  <td className="px-4 py-3 text-right text-sm">
                    <button className="mr-3 text-brand-600 hover:underline" onClick={() => setManagingMembersOf(group.id)}>
                      Members
                    </button>
                    <button className="mr-3 text-brand-600 hover:underline" onClick={() => setEditing(group)}>
                      Edit
                    </button>
                    <button className="mr-3 text-gray-500 hover:underline" onClick={() => toggleStatus(group)}>
                      {group.status === "ACTIVE" ? "Deactivate" : "Activate"}
                    </button>
                    {group.status === "INACTIVE" && (
                      <button className="text-red-600 hover:underline" onClick={() => handleDelete(group)}>
                        Delete
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && (
        <GroupFormModal
          group={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            refresh();
          }}
        />
      )}

      {managingMembersOf && (
        <GroupMembersModal
          groupId={managingMembersOf}
          onClose={() => {
            setManagingMembersOf(null);
            refresh();
          }}
        />
      )}
    </div>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">{children}</th>;
}

function GroupFormModal({ group, onClose, onSaved }: { group: Group | null; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(group?.name ?? "");
  const [description, setDescription] = useState(group?.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (group) {
        await updateGroup(group.id, { name, description });
      } else {
        await createGroup({ name, description });
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save the group.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title={group ? "Edit group" : "New group"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <div>
          <label className={labelClass}>Name</label>
          <input required value={name} onChange={(e) => setName(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Description</label>
          <textarea
            value={description ?? ""}
            onChange={(e) => setDescription(e.target.value)}
            className={inputClass}
            rows={3}
          />
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

function GroupMembersModal({ groupId, onClose }: { groupId: string; onClose: () => void }) {
  const [detail, setDetail] = useState<GroupDetail | null>(null);
  const [candidates, setCandidates] = useState<User[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function refreshDetail() {
    setDetail(await getGroup(groupId));
  }

  useEffect(() => {
    refreshDetail();
  }, [groupId]);

  useEffect(() => {
    const timeout = setTimeout(async () => {
      const page = await listUsers({ search, page_size: 20, status: "ACTIVE" });
      setCandidates(page.items);
    }, 250);
    return () => clearTimeout(timeout);
  }, [search]);

  function toggleSelected(userId: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) next.delete(userId);
      else next.add(userId);
      return next;
    });
  }

  async function handleAddSelected() {
    if (selected.size === 0) return;
    setError(null);
    setIsBusy(true);
    try {
      await addGroupUsers(groupId, Array.from(selected));
      setSelected(new Set());
      await refreshDetail();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add the users.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleRemove(userId: string) {
    setError(null);
    setIsBusy(true);
    try {
      await removeGroupUser(groupId, userId);
      await refreshDetail();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not remove the user.");
    } finally {
      setIsBusy(false);
    }
  }

  const memberIds = new Set(detail?.members.map((m) => m.id) ?? []);

  return (
    <Modal title={`Members of ${detail?.name ?? ""}`} onClose={onClose} widthClass="max-w-2xl">
      {error && <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Miembros actuales ({detail?.members.length ?? 0})</h3>
          <ul className="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
            {detail?.members.length === 0 && <li className="px-2 py-1 text-sm text-gray-400">No members.</li>}
            {detail?.members.map((member) => (
              <li key={member.id} className="flex items-center justify-between rounded-md px-2 py-1 text-sm hover:bg-gray-50">
                <span>
                  {member.full_name}
                  <span className="ml-1 text-xs text-gray-400">{member.email}</span>
                </span>
                <button
                  disabled={isBusy}
                  onClick={() => handleRemove(member.id)}
                  className="text-xs text-red-600 hover:underline disabled:opacity-50"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Add users</h3>
          <input
            className={`${inputClass} mb-2`}
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <ul className="max-h-48 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2">
            {candidates
              .filter((u) => !memberIds.has(u.id))
              .map((candidate) => (
                <li key={candidate.id} className="flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={selected.has(candidate.id)}
                    onChange={() => toggleSelected(candidate.id)}
                  />
                  <span>
                    {candidate.full_name}
                    <span className="ml-1 text-xs text-gray-400">{candidate.email}</span>
                  </span>
                </li>
              ))}
          </ul>
          <Button className="mt-2 w-full" disabled={isBusy || selected.size === 0} onClick={handleAddSelected}>
            Add {selected.size > 0 ? `(${selected.size})` : ""}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
