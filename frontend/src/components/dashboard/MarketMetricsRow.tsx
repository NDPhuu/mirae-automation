"use client";

import { useMarketOverview, useForeignTrading, usePollingControl, isMarketOpen } from "@/hooks/useMarketData";
import { ArrowUpRight, ArrowDownRight, Activity, BarChart2, TrendingUp, Globe, Zap, ZapOff } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorCard } from "@/components/ui/error-card";

export default function MarketMetricsRow() {
  const overview = useMarketOverview();
  const foreign = useForeignTrading();
  const { isLive, toggleLive } = usePollingControl();

  if (overview.error || foreign.error) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="col-span-full h-32">
        <ErrorCard
          message="Failed to load market metrics"
          onRetry={() => { overview.mutate(); foreign.mutate(); }}
        />
      </div>
    </div>
  );

  if (overview.isLoading || foreign.isLoading || !overview.data || !foreign.data) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <Skeleton key={i} className="h-[120px] w-full border border-zinc-800" />
      ))}
    </div>
  );

  const data = overview.data;
  const isUp = (data.change_point ?? 0) >= 0;
  const marketOpen = isMarketOpen();

  // Read True Foreign Net Value globally from backend
  const f_net = foreign.data.total_net_val;
  const isForeignBuy = f_net >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

      {/* 1. VN-Index Card */}
      <div className="bg-panel border border-zinc-800 shadow-md rounded-lg p-5 flex flex-col justify-center">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold text-zinc-400 flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-500" />
            {data.symbol}
          </h2>
          <div className="flex items-center gap-3">
             {/* Live Mode Toggle */}
             <button 
                onClick={toggleLive}
                title={isLive ? "Tắt Live Mode (Về tự động)" : "Bật Live Mode (Ép cập nhật)"}
                className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold transition-all border ${
                  isLive 
                  ? 'bg-brand/10 text-brand border-brand/20' 
                  : (marketOpen ? 'bg-market-up/10 text-market-up border-market-up/20' : 'bg-zinc-800 text-zinc-500 border-zinc-700 opacity-60')
                }`}
             >
                <span className={`w-1.5 h-1.5 rounded-full ${(isLive || marketOpen) ? 'bg-current animate-pulse' : 'bg-zinc-600'}`} />
                {isLive ? 'LIVE FORCED' : (marketOpen ? 'AUTO LIVE' : 'OFF-HOURS')}
             </button>
             <span className="text-[10px] text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded-full">{data.trading_date}</span>
          </div>
        </div>
        <div className="flex items-end justify-between">
          <span className={`text-3xl font-extrabold tabular-nums tracking-tighter ${isUp ? 'text-market-up' : 'text-market-down'}`}>
            {data.point?.toFixed(2)}
          </span>
          <div className={`flex items-center text-sm font-semibold ${isUp ? 'text-market-up' : 'text-market-down'}`}>
            {isUp ? <ArrowUpRight className="w-4 h-4 mr-0.5" /> : <ArrowDownRight className="w-4 h-4 mr-0.5" />}
            {isUp ? '+' : ''}{data.change_point?.toFixed(2)} ({isUp ? '+' : ''}{data.change_percent?.toFixed(2)}%)
          </div>
        </div>
      </div>

      {/* 2. Thanh khoản (Liquidity) Card */}
      <div className="bg-panel border border-zinc-800 shadow-md rounded-lg p-5 flex flex-col justify-center">
        <div className="flex items-center gap-2 mb-2">
          <BarChart2 className="w-4 h-4 text-zinc-500" />
          <h2 className="text-sm font-semibold text-zinc-400">Thanh khoản (Tỷ VNĐ)</h2>
        </div>
        <div className="flex items-end justify-between">
          <span className="text-2xl font-bold tracking-tight text-zinc-200">
            {(data.total_value ?? 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </span>
          <span className="text-sm text-zinc-500 font-medium">GTGD</span>
        </div>
        <div className="mt-1 text-xs text-zinc-500 flex justify-between">
          <span>Khối lượng:</span>
          <span className="text-zinc-300 font-medium">{(data.total_volume ?? 0).toLocaleString()} CP</span>
        </div>
      </div>

      {/* 3. Độ rộng (Breadth) Card */}
      <div className="bg-panel border border-zinc-800 shadow-md rounded-lg p-5 flex flex-col justify-center">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-4 h-4 text-zinc-500" />
          <h2 className="text-sm font-semibold text-zinc-400">Độ rộng thị trường</h2>
        </div>

        <div className="flex justify-between text-xs font-semibold mb-1">
          <span className="text-market-up">{(data.breadth_ceiling || 0) + (data.breadth_green || 0)}</span>
          <span className="text-market-ref">{data.breadth_yellow}</span>
          <span className="text-market-down">{(data.breadth_floor || 0) + (data.breadth_red || 0)}</span>
        </div>

        <div className="flex h-2 rounded-full overflow-hidden opacity-90 w-full mb-1 border border-zinc-800">
          <div style={{ flex: (data.breadth_ceiling || 0) + (data.breadth_green || 0) }} className="bg-market-up" />
          <div style={{ flex: (data.breadth_yellow || 0) }} className="bg-market-ref" />
          <div style={{ flex: (data.breadth_floor || 0) + (data.breadth_red || 1) }} className="bg-market-down" />
        </div>
      </div>

      {/* 4. Khối ngoại (Foreign) Card */}
      <div className="bg-panel border border-zinc-800 shadow-md rounded-lg p-5 flex flex-col justify-center">
        <div className="flex items-center gap-2 mb-2">
          <Globe className="w-4 h-4 text-zinc-500" />
          <h2 className="text-sm font-semibold text-zinc-400">Giao dịch khối ngoại</h2>
        </div>
        <div className="flex items-end justify-between">
          <span className={`text-2xl font-bold tracking-tight ${isForeignBuy ? 'text-market-up' : 'text-market-down'}`}>
            {isForeignBuy ? '+' : ''}{(f_net / 1000000000).toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </span>
          <span className="text-sm text-zinc-500 font-medium">Tỷ VNĐ</span>
        </div>
        <div className="mt-1 flex justify-between">
          <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded-sm ${isForeignBuy ? 'bg-market-up/20 text-market-up' : 'bg-market-down/20 text-market-down'}`}>
            {isForeignBuy ? 'Mua ròng' : 'Bán ròng'}
          </span>
        </div>
      </div>

    </div>
  );
}
