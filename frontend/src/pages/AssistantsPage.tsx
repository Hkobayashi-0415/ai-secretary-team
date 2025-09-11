// frontend/src/pages/AssistantsPage.tsx
import React, { useEffect, useState } from "react";
import { API_BASE_URL as BASE } from "../api/client";

type Assistant = {
  id: string;
  name: string;
  description: string;
  default_llm_model: string;
};

export default function AssistantsPage() {
  const [list, setList] = useState<Assistant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: "",
    description: "",
    default_llm_model: "gemini-pro",
  });
  const [posting, setPosting] = useState(false);

  const [deletingId, setDeletingId] = useState<string | null>(null);

  // 編集用
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    name: "",
    description: "",
    default_llm_model: "gemini-pro",
  });
  const [savingId, setSavingId] = useState<string | null>(null);

  async function fetchList() {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${BASE}/assistants/`);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      setList(data);
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchList();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name は必須です");
      return;
    }
    try {
      setPosting(true);
      setError(null);
      let res = await fetch(`${BASE}/assistants/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        // 末尾スラッシュ無しにもトライ
        res = await fetch(`${BASE}/assistants`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
      }
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status}: ${text}`);
      }
      setForm({ name: "", description: "", default_llm_model: "gemini-pro" });
      await fetchList();
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setPosting(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("この Assistant を削除します。よろしいですか？")) return;
    try {
      setDeletingId(id);
      setError(null);
      let res = await fetch(`${BASE}/assistants/${id}`, { method: "DELETE" });
      if (!res.ok) res = await fetch(`${BASE}/assistants/${id}/`, { method: "DELETE" });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status}: ${text}`);
      }
      setList((prev) => prev.filter((a) => a.id !== id));
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setDeletingId(null);
    }
  }

  function startEdit(a: Assistant) {
    setEditingId(a.id);
    setEditForm({
      name: a.name ?? "",
      description: a.description ?? "",
      default_llm_model: a.default_llm_model ?? "gemini-pro",
    });
    setError(null);
  }

  function cancelEdit() {
    setEditingId(null);
  }

  async function handleSave(id: string) {
    if (!editForm.name.trim()) {
      setError("Name は必須です");
      return;
    }
    try {
      setSavingId(id);
      setError(null);
      const payload = {
        name: editForm.name,
        description: editForm.description,
        default_llm_model: editForm.default_llm_model,
      };

      // PUT → 末尾スラッシュ付き → PATCH の順でトライ
      let res = await fetch(`${BASE}/assistants/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        res = await fetch(`${BASE}/assistants/${id}/`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      if (!res.ok) {
        res = await fetch(`${BASE}/assistants/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      if (!res.ok) {
        res = await fetch(`${BASE}/assistants/${id}/`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status}: ${text}`);
      }

      // 成功：ローカル状態を更新（再取得でもOK）
      const updated = await res.json().catch(() => payload);
      setList((prev) =>
        prev.map((a) => (a.id === id ? ({ ...a, ...updated } as Assistant) : a))
      );
      setEditingId(null);
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div style={{ padding: "1rem" }}>
      <h1>AI Assistants Management</h1>

      {/* 作成フォーム */}
      <form
        data-testid="assistant-create-form"
        onSubmit={handleSubmit}
        style={{ margin: "1rem 0" }}
      >
        <fieldset disabled={posting} style={{ border: "1px solid #ddd", padding: "1rem", borderRadius: 8 }}>
          <legend style={{ padding: "0 .5rem" }}>Create Assistant</legend>
          <div style={{ marginBottom: ".5rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>Name *</label>
            <input
              data-testid="assistant-create-name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="例: Demo Assistant"
              style={{ width: "100%", padding: ".5rem" }}
            />
          </div>
          <div style={{ marginBottom: ".5rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>Description</label>
            <input
              data-testid="assistant-create-description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="短い説明"
              style={{ width: "100%", padding: ".5rem" }}
            />
          </div>
          <div style={{ marginBottom: ".75rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>Default LLM Model</label>
            <select
              data-testid="assistant-create-model"
              value={form.default_llm_model}
              onChange={(e) => setForm({ ...form, default_llm_model: e.target.value })}
              style={{ width: "100%", padding: ".5rem" }}
            >
              <option value="gemini-pro">gemini-pro</option>
              <option value="gpt-4">gpt-4</option>
              <option value="claude-3-opus">claude-3-opus</option>
            </select>
          </div>
          <button
            data-testid="assistant-create-submit"
            type="submit"
            disabled={posting}
            style={{ padding: ".5rem 1rem" }}
          >
            {posting ? "Creating..." : "Create"}
          </button>
        </fieldset>
      </form>

      {/* エラー表示 */}
      {error && (
        <div data-testid="assistant-error" style={{ color: "crimson", marginBottom: "1rem" }}>
          Error: {error}
        </div>
      )}

      {/* 一覧 */}
      <h2>Existing Assistants</h2>
      {loading ? (
        <p>Loading...</p>
      ) : list.length === 0 ? (
        <p>まだありません</p>
      ) : (
        <ul data-testid="assistants-list">
          {list.map((a) => {
            const isEditing = editingId === a.id;
            return (
              <li
                key={a.id}
                data-testid={`assistant-row-${a.id}`}
                style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}
              >
                <div style={{ flex: 1, minWidth: 260 }}>
                  {isEditing ? (
                    <div style={{ display: "grid", gap: 6 }}>
                      <input
                        data-testid="assistant-edit-name"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        placeholder="Name"
                        style={{ padding: ".4rem" }}
                      />
                      <input
                        data-testid="assistant-edit-description"
                        value={editForm.description}
                        onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                        placeholder="Description"
                        style={{ padding: ".4rem" }}
                      />
                      <select
                        data-testid="assistant-edit-model"
                        value={editForm.default_llm_model}
                        onChange={(e) => setEditForm({ ...editForm, default_llm_model: e.target.value })}
                        style={{ padding: ".4rem" }}
                      >
                        <option value="gemini-pro">gemini-pro</option>
                        <option value="gpt-4">gpt-4</option>
                        <option value="claude-3-opus">claude-3-opus</option>
                      </select>
                    </div>
                  ) : (
                    <div>
                      <strong>{a.name}</strong> — {a.description} <em>({a.default_llm_model})</em>
                    </div>
                  )}
                </div>

                <div style={{ display: "flex", gap: 8 }}>
                  {isEditing ? (
                    <>
                      <button
                        data-testid="assistant-save"
                        onClick={() => handleSave(a.id)}
                        disabled={savingId === a.id}
                        style={{ padding: ".25rem .75rem" }}
                      >
                        {savingId === a.id ? "Saving..." : "Save"}
                      </button>
                      <button
                        data-testid="assistant-cancel"
                        onClick={cancelEdit}
                        style={{ padding: ".25rem .75rem" }}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        data-testid="assistant-edit"
                        onClick={() => startEdit(a)}
                        style={{ padding: ".25rem .75rem" }}
                      >
                        Edit
                      </button>
                      <button
                        data-testid="assistant-delete"
                        onClick={() => handleDelete(a.id)}
                        disabled={deletingId === a.id}
                        style={{ padding: ".25rem .75rem" }}
                      >
                        {deletingId === a.id ? "Deleting..." : "Delete"}
                      </button>
                    </>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
