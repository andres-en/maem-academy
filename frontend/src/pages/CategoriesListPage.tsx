import { useEffect, useState } from "react";
import { Button } from "../components/ui/Button";
import { StatusBadge } from "../components/ui/Badge";
import { Modal } from "../components/ui/Modal";
import { inputClass, labelClass } from "../components/ui/formStyles";
import { useAuth } from "../contexts/AuthContext";
import { ApiError } from "../services/apiClient";
import { createCategory, deleteCategory, listCategories, setCategoryStatus, updateCategory } from "../services/categories";
import type { Category } from "../types";

export function CategoriesListPage() {
  const { hasRole } = useAuth();
  const canManage = hasRole("SUPERADMIN", "ADMIN");
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editing, setEditing] = useState<Category | "new" | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function refresh() {
    setIsLoading(true);
    try {
      setCategories(await listCategories());
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function toggleStatus(category: Category) {
    const newStatus = category.status === "ACTIVE" ? "INACTIVE" : "ACTIVE";
    await setCategoryStatus(category.id, newStatus);
    refresh();
  }

  async function handleDelete(category: Category) {
    if (!confirm(`Permanently delete the category "${category.name}"? This action cannot be undone.`)) return;
    setDeleteError(null);
    try {
      await deleteCategory(category.id);
      refresh();
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Could not delete the category.");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Categories</h1>
          <p className="mt-1 text-sm text-gray-500">Course classification by client or topic</p>
        </div>
        {canManage && <Button onClick={() => setEditing("new")}>New category</Button>}
      </div>

      {deleteError && <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</div>}

      <div className="mt-6 overflow-hidden rounded-xl border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <Th>Name</Th>
              <Th>Description</Th>
              <Th>Status</Th>
              {canManage && <Th />}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-400">
                  Loading...
                </td>
              </tr>
            )}
            {!isLoading && categories.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-400">
                  No categories yet.
                </td>
              </tr>
            )}
            {categories.map((category) => (
              <tr key={category.id}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {category.name}
                  {category.name === "GENERAL" && (
                    <span className="ml-2 rounded bg-brand-50 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-brand-600">
                      Predeterminada
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{category.description || "—"}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={category.status} />
                </td>
                {canManage && (
                  <td className="px-4 py-3 text-right text-sm">
                    <button className="mr-3 text-brand-600 hover:underline" onClick={() => setEditing(category)}>
                      Edit
                    </button>
                    <button className="mr-3 text-gray-500 hover:underline" onClick={() => toggleStatus(category)}>
                      {category.status === "ACTIVE" ? "Deactivate" : "Activate"}
                    </button>
                    {category.status === "INACTIVE" && category.name !== "GENERAL" && (
                      <button className="text-red-600 hover:underline" onClick={() => handleDelete(category)}>
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
        <CategoryFormModal
          category={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
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

function CategoryFormModal({
  category,
  onClose,
  onSaved,
}: {
  category: Category | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [name, setName] = useState(category?.name ?? "");
  const [description, setDescription] = useState(category?.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (category) {
        await updateCategory(category.id, { name, description });
      } else {
        await createCategory({ name, description });
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save the category.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title={category ? "Edit category" : "New category"} onClose={onClose}>
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
