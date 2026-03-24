"use client";

import { useForeignTrading, useSyncStatus } from "@/hooks/useMarketData";
import { useState } from "react";
import api from "@/lib/api";

export default function ForeignActivityPanel() {
  const { data, isLoading, error } = useForeignTrading();
  const { data: syncStatus, mutate: mutateSync } = useSyncStatus();
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    const now = new Date();
    const isEarly = now.getHours() < 15 || (now.getHours() === 15 && now.getMinutes() < 10);
    
    if (isEarly) {
      if (!confirm("⚠️ Thị trường chưa chốt xong ATC (trước 15:10). Dữ liệu có thể bị sai lệch. Bạn vẫn muốn tiếp tục?")) {
        return;
      }
    }

    try {
      setIsSyncing(true);
      await api.post("/sync-eod");
      mutateSync();
    } catch (err) {
      alert("Lỗi khởi động Sync: " + err);
    } finally {
      setIsSyncing(false);
    }
  };

  if (isLoading) return <div className="h-48 bg-panel animate-pulse rounded-lg border border-panel-border"></div>;
  if (error || !data) return <div className="h-48 bg-panel rounded-lg border border-panel-border flex items-center justify-center text-red-500">Failed to load data</div>;

  const isRunning = syncStatus?.status === 'running';
  const isEOD = syncStatus?.type === 'EOD' && syncStatus?.status === 'completed';
  const isIntraday = syncStatus?.type === 'INTRADAY' && syncStatus?.status === 'completed';

  return (
    <div className="bg-panel border border-panel-border rounded-lg shadow-xl overflow-hidden flex flex-col">
      <div className="p-4 border-b border-panel-border bg-[#1a1a1a] flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-gray-200">Khối ngoại Mua/Bán</h3>
            {isEOD && <span className="text-[10px] bg-market-up/10 text-market-up px-1.5 py-0.5 rounded border border-market-up/20 font-bold">EOD CHỐT</span>}
            {isIntraday && <span className="text-[10px] bg-market-up/10 text-market-up px-1.5 py-0.5 rounded border border-market-up/20 font-bold italic">TẠM THỜI</span>}
          </div>
          {data.top_buy.length > 0 && (
            <span className="text-[10px] text-zinc-500 font-mono">Session: {data.top_buy[0].trading_date}</span>
          )}
        </div>
        
        <button 
          onClick={handleSync}
          disabled={isRunning || isSyncing}
          className={`px-3 py-1.5 rounded text-xs font-black tracking-tight shadow-lg transition-all ${
            isRunning 
              ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
              : isEOD
                ? 'bg-market-up text-black'
                : 'bg-market-up/20 text-market-up hover:bg-market-up/30 border border-market-up/30'
          }`}
        >
          {isRunning ? 'Đang sync...' : isEOD ? 'Đã Chốt EOD' : 'Chốt EOD Sync'}
        </button>
      </div>

      {/* Real Progress Bar */}
      {isRunning && (
        <div className="bg-[#1a1a1a] px-4 pb-3">
          <div className="flex justify-between text-[10px] mb-1">
            <span className="text-zinc-400">Đang quét {syncStatus.type}: {syncStatus.processed}/{syncStatus.total} mã</span>
            <span className="text-market-up font-mono">~{Math.round(syncStatus.eta_seconds / 60)} phút</span>
          </div>
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-market-up transition-all duration-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" 
              style={{ width: `${(syncStatus.processed / syncStatus.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex-1 divide-y divide-panel-border">
        {/* Top Mua */}
        <div className="p-3">
          <div className="text-xs font-semibold text-market-up mb-2 uppercase tracking-tight">Top Mua</div>
          <div className="space-y-2">
            {data.top_buy.slice(0, 6).map((item) => (
              <div key={item.symbol} className="flex items-center justify-between text-sm">
                <span className="font-bold text-gray-300 w-12">{item.symbol}</span>
                {/* Progress bar visual */}
                <div className="flex-1 mx-3 h-1.5 bg-[#262626] rounded-full overflow-hidden">
                  <div className="h-full bg-market-up opacity-80" style={{ width: `${Math.min((item.net_val / 1e9 / 600) * 100, 100)}%` }} />
                </div>
                <span className="font-medium text-market-up text-right tabular-nums">{(item.net_val / 1e9).toFixed(2)} Tỷ</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Bán */}
        <div className="p-3">
          <div className="text-xs font-semibold text-market-down mb-2 uppercase tracking-tight">Top Bán</div>
          <div className="space-y-2">
            {data.top_sell.slice(0, 6).map((item) => (
              <div key={item.symbol} className="flex items-center justify-between text-sm">
                <span className="font-bold text-gray-300 w-12">{item.symbol}</span>
                <div className="flex-1 mx-3 h-1.5 bg-[#262626] rounded-full overflow-hidden flex justify-end">
                  <div className="h-full bg-market-down opacity-80" style={{ width: `${Math.min((Math.abs(item.net_val / 1e9) / 600) * 100, 100)}%` }} />
                </div>
                <span className="font-medium text-market-down text-right tabular-nums">{(item.net_val / 1e9).toFixed(2)} Tỷ</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
