import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import type { Document, Category } from "../types";

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const navigate = useNavigate();

  const loadDocuments = () => {
    client
      .get(`/documents/?page=${page}`)
      .then((res) => {
        setDocuments(res.data.results);
        setTotalCount(res.data.count);
      })
      .catch((err) => {
        console.error(err);
        setError("خطا در دریافت اسناد.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocuments();
  }, [page]);

  useEffect(() => {
    client
      .get("/categories/")
      .then((res) => setCategories(res.data.results))
      .catch((err) => console.error(err));
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title || !category) return;

    setUploading(true);
    setError("");
    const formData = new FormData();
    formData.append("title", title);
    formData.append("description", description);
    formData.append("category", category);
    formData.append("file", file);

    try {
      await client.post("/documents/", formData);
      setTitle("");
      setDescription("");
      setCategory("");
      setFile(null);
      setPage(1);
      loadDocuments();
    } catch (err: any) {
      console.error("Upload error:", JSON.stringify(err.response?.data, null, 2));
      setError("آپلود ناموفق بود.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("این سند حذف شود؟")) return;
    try {
      await client.delete(`/documents/${id}/`);
      loadDocuments();
    } catch (err) {
      console.error(err);
      setError("حذف ناموفق بود.");
    }
  };

  if (loading) return <p>در حال بارگذاری...</p>;

  const totalPages = Math.ceil(totalCount / 10);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Documents</h1>

      <form onSubmit={handleUpload} className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">آپلود سند جدید</h2>
        <input
          type="text"
          placeholder="عنوان"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 mb-3"
          required
        />
        <textarea
          placeholder="توضیحات"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 mb-3"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 mb-3"
          required
        >
          <option value="">انتخاب دسته‌بندی</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full mb-3"
          required
        />
        <button
          type="submit"
          disabled={uploading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {uploading ? "در حال آپلود..." : "آپلود"}
        </button>
        {error && <p className="text-red-600 mt-3 text-sm">{error}</p>}
      </form>

      {documents.length === 0 ? (
        <p className="text-gray-500">هنوز سندی آپلود نشده.</p>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white p-4 rounded-lg shadow flex items-center justify-between"
            >
              <div
                className="flex-1 cursor-pointer"
                onClick={() => navigate(`/documents/${doc.id}`)}
              >
                <h2 className="font-semibold">{doc.title}</h2>
                <p className="text-sm text-gray-500">{doc.file_name}</p>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    doc.status === "INDEXED"
                      ? "bg-green-100 text-green-700"
                      : doc.status === "FAILED"
                      ? "bg-red-100 text-red-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {doc.status}
                </span>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  حذف
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span>
            صفحه {page} از {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}