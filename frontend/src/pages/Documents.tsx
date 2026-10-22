import { useEffect, useState } from "react";
import client from "../api/client";
import type { Document, Category, PaginatedResponse } from "../types";

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Pagination & Filters
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");

  // Upload Modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // Detail Modal state
  const [activeDoc, setActiveDoc] = useState<Document | null>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      let url = `/documents/?page=${page}`;
      if (selectedCategory) url += `&category=${selectedCategory}`;
      if (searchQuery.trim()) url += `&search=${encodeURIComponent(searchQuery.trim())}`;

      const res = await client.get<PaginatedResponse<Document>>(url);
      setDocuments(res.data.results);
      setTotalCount(res.data.count);
    } catch (err: any) {
      console.error(err);
      setError("خطا در بارگذاری اسناد.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [page, selectedCategory]);

  useEffect(() => {
    client
      .get<PaginatedResponse<Category>>("/categories/")
      .then((res) => setCategories(res.data.results))
      .catch((err) => console.error(err));
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadDocuments();
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title.trim() || !category) return;

    setUploading(true);
    setError("");
    setSuccess("");

    const formData = new FormData();
    formData.append("title", title.trim());
    formData.append("description", description.trim());
    formData.append("category", category);
    formData.append("file", file);

    try {
      await client.post("/documents/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSuccess("سند با موفقیت بارگذاری شد و در حال پردازش است.");
      setTitle("");
      setDescription("");
      setCategory("");
      setFile(null);
      setShowUploadModal(false);
      setPage(1);
      loadDocuments();
    } catch (err: any) {
      console.error("Upload error:", err.response?.data);
      const data = err.response?.data;
      if (data && typeof data === "object") {
        const firstKey = Object.keys(data)[0];
        const val = data[firstKey];
        setError(`${firstKey}: ${Array.isArray(val) ? val[0] : val}`);
      } else {
        setError("آپلود ناموفق بود. لطفاً فرمت و حجم فایل را بررسی کنید.");
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number, docTitle: string) => {
    if (!confirm(`آیا از حذف سند «${docTitle}» اطمینان دارید؟`)) return;

    try {
      await client.delete(`/documents/${id}/`);
      setSuccess("سند با موفقیت حذف شد.");
      if (activeDoc?.id === id) setActiveDoc(null);
      loadDocuments();
    } catch (err) {
      console.error(err);
      setError("حذف سند با خطا مواجه شد.");
    }
  };

  const getStatusBadge = (status: Document["status"]) => {
    switch (status) {
      case "INDEXED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>ایندکس شده (آماده AI)</span>;
      case "PROCESSING":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse"><span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>در حال پردازش</span>;
      case "PROCESSED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200"><span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>متن استخراج شد</span>;
      case "FAILED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200"><span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>خطا در پردازش</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">آپلود شده</span>;
    }
  };

  const totalPages = Math.ceil(totalCount / 10);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">مدیریت اسناد و مدارک</h1>
          <p className="text-sm text-slate-500 mt-1">
            آپلود، مشاهده متن استخراج‌شده، و وضعیت ایندکس فایل‌ها برای هوش مصنوعی
          </p>
        </div>
        <button
          onClick={() => {
            setError("");
            setSuccess("");
            setShowUploadModal(true);
          }}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm hover:from-indigo-700 hover:to-purple-700 shadow-md shadow-indigo-500/20 transition-all hover:-translate-y-0.5"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          آپلود سند جدید
        </button>
      </div>

      {/* Notifications */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-rose-500 hover:text-rose-700 text-lg">×</button>
        </div>
      )}
      {success && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess("")} className="text-emerald-500 hover:text-emerald-700 text-lg">×</button>
        </div>
      )}

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearch} className="flex-1 w-full flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="جستجو در عنوان یا متن اسناد..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-4 pr-10 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-sm"
            />
            <svg className="w-4 h-4 text-slate-400 absolute right-3.5 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium transition-colors"
          >
            جستجو
          </button>
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(1);
            }}
            className="w-full md:w-48 px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 text-sm bg-white"
          >
            <option value="">همه دسته‌بندی‌ها</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("");
              setPage(1);
            }}
            title="بازنشانی فیلترها"
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Documents List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm">در حال بارگذاری اسناد...</div>
      ) : documents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-500 mx-auto flex items-center justify-center mb-4">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-base font-bold text-slate-800 mb-1">هیچ سندی پیدا نشد</h3>
          <p className="text-sm text-slate-500 mb-6">با دکمه زیر اولین مدرک خود را در سیستم ثبت کنید.</p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-sm hover:bg-indigo-700"
          >
            آپلود اولین سند
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              <div
                className="flex items-start gap-4 flex-1 cursor-pointer"
                onClick={() => setActiveDoc(doc)}
              >
                <div className="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-bold text-slate-900 text-base hover:text-indigo-600 transition-colors">
                      {doc.title}
                    </h3>
                    {getStatusBadge(doc.status)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-1">{doc.description || "بدون توضیحات"}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                    <span>{doc.file_name}</span>
                    <span>•</span>
                    <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                    <span>•</span>
                    <span>{new Date(doc.created_at).toLocaleDateString("fa-IR")}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                <button
                  onClick={() => setActiveDoc(doc)}
                  className="px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-medium transition-colors border border-slate-200"
                >
                  مشاهده جزئیات و متن
                </button>
                <button
                  onClick={() => handleDelete(doc.id, doc.title)}
                  title="حذف سند"
                  className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-3 pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-medium disabled:opacity-40 hover:bg-slate-50 shadow-sm"
          >
            قبلی
          </button>
          <span className="text-xs text-slate-600 font-medium">
            صفحه {page} از {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-medium disabled:opacity-40 hover:bg-slate-50 shadow-sm"
          >
            بعدی
          </button>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-slate-900">آپلود سند جدید</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  عنوان سند <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="مثال: قرارداد همکاری شرکت، راهنمای API..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  دسته‌بندی <span className="text-rose-500">*</span>
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-sm bg-white"
                  required
                >
                  <option value="">انتخاب دسته‌بندی</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">توضیحات</label>
                <textarea
                  placeholder="خلاصه‌ای از محتوا یا توضیحات اضافی..."
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  فایل سند (PDF, Word, Image) <span className="text-rose-500">*</span>
                </label>
                <div className="border-2 border-dashed border-slate-300 hover:border-indigo-500 rounded-2xl p-6 text-center transition-colors">
                  <input
                    type="file"
                    id="file-upload"
                    accept=".pdf,.docx,.jpg,.jpeg,.png"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="hidden"
                    required
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="w-10 h-10 rounded-full bg-indigo-50 text-indigo-600 mx-auto flex items-center justify-center mb-2">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    {file ? (
                      <p className="text-sm font-semibold text-indigo-600 truncate">{file.name}</p>
                    ) : (
                      <>
                        <p className="text-sm font-medium text-slate-700">کلیک کنید یا فایل را بکشید و رها کنید</p>
                        <p className="text-xs text-slate-400 mt-1">حداکثر ۱۰ مگابایت (PDF, Word, JPG, PNG)</p>
                      </>
                    )}
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-100"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={uploading || !file || !title.trim() || !category}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md shadow-indigo-500/20 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>در حال آپلود و پردازش...</span>
                    </>
                  ) : (
                    <span>آپلود و ذخیره</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Detail Modal */}
      {activeDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 border border-slate-100 max-h-[90vh] flex flex-col">
            <div className="flex items-start justify-between pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-lg font-bold text-slate-900">{activeDoc.title}</h3>
                  {getStatusBadge(activeDoc.status)}
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  فایل: {activeDoc.file_name} • {(activeDoc.file_size / 1024).toFixed(1)} KB • تاریخ ثبت: {new Date(activeDoc.created_at).toLocaleDateString("fa-IR")}
                </p>
              </div>
              <button
                onClick={() => setActiveDoc(null)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="my-4 overflow-y-auto flex-1 space-y-4 pr-1">
              {activeDoc.description && (
                <div>
                  <h4 className="text-xs font-bold text-slate-500 mb-1">توضیحات:</h4>
                  <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {activeDoc.description}
                  </p>
                </div>
              )}

              {activeDoc.error_message && (
                <div>
                  <h4 className="text-xs font-bold text-rose-600 mb-1">پیام خطا در پردازش:</h4>
                  <p className="text-xs text-rose-700 bg-rose-50 p-3 rounded-xl border border-rose-200">
                    {activeDoc.error_message}
                  </p>
                </div>
              )}

              <div>
                <h4 className="text-xs font-bold text-slate-500 mb-1">متن استخراج‌شده (برای AI):</h4>
                {activeDoc.extracted_text ? (
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed max-h-64 overflow-y-auto whitespace-pre-wrap font-sans">
                    {activeDoc.extracted_text}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">هنوز متنی برای این سند استخراج نشده است.</p>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleDelete(activeDoc.id, activeDoc.title)}
                className="text-xs font-medium text-rose-600 hover:text-rose-700 flex items-center gap-1"
              >
                حذف این سند
              </button>
              <button
                onClick={() => setActiveDoc(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-medium hover:bg-slate-200"
              >
                بستن
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}