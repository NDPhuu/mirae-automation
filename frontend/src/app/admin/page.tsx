'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { 
  ShieldCheckIcon, 
  CpuChipIcon, 
  CircleStackIcon, 
  TrashIcon, 
  StopIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const fetcher = (url: string) => fetch(url, {
  headers: { 'X-API-KEY': process.env.NEXT_PUBLIC_API_KEY || 'mirae-dev-key' }
}).then(res => res.json());

export default function AdminDashboard() {
  const router = useRouter();
  const [isCleaning, setIsCleaning] = useState(false);
  const [isStopping, setIsStopping] = useState(false);

  // Authentication Guard
  useEffect(() => {
    const userRole = document.cookie.split('; ').find(row => row.startsWith('user_role='))?.split('=')[1];
    if (userRole !== 'admin') {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    document.cookie = "user_role=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    localStorage.removeItem('user_role');
    router.push('/login');
  };

  const { data: stats, error, mutate } = useSWR(`${process.env.NEXT_PUBLIC_API_URL}/admin/stats`, fetcher, {
    refreshInterval: 5000 // Refresh every 5s
  });

  const handleCleanup = async () => {
    if (!confirm('Bạn có chắc chắn muốn dọn dẹp dữ liệu cũ (>30 ngày) và backup lên R2?')) return;
    setIsCleaning(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/system/cleanup`, {
        method: 'POST',
        headers: { 'X-API-KEY': process.env.NEXT_PUBLIC_API_KEY || 'mirae-dev-key' }
      });
      const result = await res.json();
      alert(result.message || 'Dọn dẹp hoàn tất');
    } catch (err) {
      alert('Lỗi khi dọn dẹp hệ thống');
    } finally {
      setIsCleaning(false);
      mutate();
    }
  };

  const handleStopStreams = () => {
    alert('Chức năng này sẽ ngắt toàn bộ kết nối DNSE/SSI ngay lập tức để giải phóng RAM.');
    // API logic for stopping streams could be added here
  };

  if (!stats && !error) return <div className="p-8 text-zinc-500">Đang tải thông số hệ thống...</div>;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#ededed] p-6 lg:p-10 font-sans">
      <div className="max-w-6xl mx-auto space-y-10">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-brand mb-1">
              <ShieldCheckIcon className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-wider">Hệ thống Quản trị</span>
            </div>
            <h1 className="text-3xl font-bold">Admin Control Center</h1>
          </div>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 transition-colors text-sm text-zinc-400 hover:text-white"
          >
            Đăng xuất
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard 
            title="Sử dụng RAM" 
            value={`${stats?.ram_usage_mb || 0} MB`} 
            subtitle="Current Python RSS"
            icon={<CpuChipIcon className="w-6 h-6 text-brand" />}
            status={stats?.ram_usage_mb > 450 ? 'danger' : 'normal'}
          />
          <StatCard 
            title="Dung lượng Database" 
            value={`${stats?.db_size_mb || 0} MB`} 
            subtitle="SQLite mirae_asset.db"
            icon={<CircleStackIcon className="w-6 h-6 text-[#f7ca49]" />}
          />
          <StatCard 
            title="Trạng thái Ingestion" 
            value={stats?.ingestion_status?.state || 'IDLE'} 
            subtitle={stats?.ingestion_status?.message || 'Sẵn sàng'}
            icon={<ArrowPathIcon className={`w-6 h-6 ${stats?.ingestion_status?.state === 'SYNCING' ? 'animate-spin text-brand' : 'text-zinc-500'}`} />}
          />
        </div>

        {/* Maintenance Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-[#141414] border border-[#262626] rounded-2xl p-6 space-y-6 shadow-2xl">
            <h2 className="text-xl font-bold flex items-center gap-2 text-white/90">
              <ExclamationTriangleIcon className="w-5 h-5 text-brand" />
              Bảo trì Hệ thống
            </h2>
            <div className="space-y-4">
              <ActionButton 
                onClick={handleCleanup}
                loading={isCleaning}
                title="Dọn dẹp & Lưu trữ (30 Ngày)"
                description="Gom dữ liệu cũ đẩy lên R2 và giải phóng dung lượng DB."
                icon={<TrashIcon className="w-5 h-5" />}
                variant="primary"
              />
              <ActionButton 
                onClick={handleStopStreams}
                loading={isStopping}
                title="Ngắt kết nối Khẩn cấp"
                description="Dừng toàn bộ luồng dữ liệu thời gian thực để hạ RAM."
                icon={<StopIcon className="w-5 h-5" />}
                variant="danger"
              />
            </div>
          </div>

          <div className="bg-[#141414] border border-[#262626] rounded-2xl p-6 overflow-hidden">
            <h2 className="text-xl font-bold mb-4">Lịch sử Hoạt động (Logs)</h2>
            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
              <LogItem level="INFO" msg="Scheduler started: AutoSync 15:05" time="16:42" />
              <LogItem level="ERROR" msg="SSI Rate Limit (429) - Automatic retry in 5s" time="15:12" />
              <LogItem level="SUCCESS" msg="EOD Sync Completed: 350 symbols updated" time="15:25" />
              <LogItem level="INFO" msg="Market Curfew: Disconnected real-time streams" time="17:30" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon, status }: any) {
  return (
    <div className="bg-[#141414] border border-[#262626] p-6 rounded-2xl space-y-4">
      <div className="flex justify-between items-start">
        <div className="p-2 bg-white/5 rounded-lg">{icon}</div>
        {status === 'danger' && <span className="bg-red-500/20 text-red-500 text-[10px] font-bold px-2 py-1 rounded-full animate-pulse">OVERLOAD</span>}
      </div>
      <div>
        <h3 className="text-zinc-500 text-sm font-medium">{title}</h3>
        <p className="text-2xl font-bold mt-1">{value}</p>
        <p className="text-xs text-zinc-600 mt-1">{subtitle}</p>
      </div>
    </div>
  );
}

function ActionButton({ onClick, loading, title, description, icon, variant }: any) {
  const baseClass = "w-full flex items-start gap-4 p-4 rounded-xl border transition-all active:scale-[0.98]";
  const variantClass = variant === 'primary' 
    ? "bg-white/5 border-white/5 hover:bg-white/10" 
    : "bg-red-500/5 border-red-500/10 hover:bg-red-500/10 hover:border-red-500/20 group";

  return (
    <button onClick={onClick} disabled={loading} className={`${baseClass} ${variantClass}`}>
      <div className={`p-2 rounded-lg ${variant === 'primary' ? 'bg-zinc-800' : 'bg-red-500/20 text-red-500'}`}>
        {loading ? <ArrowPathIcon className="w-5 h-5 animate-spin" /> : icon}
      </div>
      <div className="text-left">
        <p className="font-semibold text-sm">{title}</p>
        <p className="text-xs text-zinc-500 mt-1">{description}</p>
      </div>
    </button>
  );
}

function LogItem({ level, msg, time }: any) {
  const color = level === 'ERROR' ? 'text-market-down' : level === 'SUCCESS' ? 'text-market-up' : 'text-zinc-500';
  return (
    <div className="flex items-start gap-3 p-3 bg-black/20 rounded-lg text-xs border border-white/5">
      <span className="text-zinc-600 font-mono">{time}</span>
      <span className={`font-bold min-w-[50px] ${color}`}>{level}</span>
      <span className="text-zinc-400">{msg}</span>
    </div>
  );
}
