export default function Dashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-500 text-sm">تعداد اسناد</p>
          <p className="text-3xl font-bold">--</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-500 text-sm">دسته‌بندی‌ها</p>
          <p className="text-3xl font-bold">--</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-500 text-sm">در حال پردازش</p>
          <p className="text-3xl font-bold">--</p>
        </div>
      </div>
    </div>
  );
}