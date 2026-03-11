"use client";

import { useMarketOverview } from "@/hooks/useMarketData";
import { ArrowUpRight, ArrowDownRight, Activity } from "lucide-react";

export default function MarketOverviewCard() {
  const { data, isLoading, error } = useMarketOverview();

  if (isLoading) return <div className="h-32 bg-panel animate-pulse rounded-lg border border-panel-border"></div>;
  if (error || !data) return <div className="h-32 bg-panel rounded-lg border border-panel-border flex items-center justify-center text-red-500">Failed to load data</div>;

  const isUp = (data.change_point ?? 0) >= 0;

  return (
    <div className="bg-panel border border-panel-border rounded-lg p-5 flex flex-col justify-between shadow-xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-gray-400" />
            {data.symbol}
          </h2>
          <p className="text-xs text-gray-500 mt-1">Date: {data.trading_date}</p>
        </div>
        <div className="text-right">
          <div className={`text-4xl font-extrabold tabular-nums tracking-tighter ${isUp ? 'text-market-up' : 'text-market-down'}`}>
            {data.point?.toFixed(2)}
          </div>
          <div className={`flex items-center justify-end font-semibold text-sm mt-1 ${isUp ? 'text-market-up' : 'text-market-down'}`}>
            {isUp ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
            {isUp ? '+' : ''}{data.change_point?.toFixed(2)} ({isUp ? '+' : ''}{data.change_percent?.toFixed(2)}%)
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t border-panel-border">
        <div>
          <p className="text-xs text-gray-500 uppercase font-semibold">Volume</p>
          <p className="text-sm font-medium text-gray-200 mt-0.5">{(data.total_volume ?? 0).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase font-semibold">Value (VND)</p>
          <p className="text-sm font-medium text-gray-200 mt-0.5">{(data.total_value ?? 0).toLocaleString()}</p>
        </div>
      </div>

      {/* Market Breadth Line */}
      <div className="mt-4 flex h-1.5 rounded-full overflow-hidden opacity-90">
        <div style={{ flex: (data.breadth_ceiling || 0) + (data.breadth_green || 0) }} className="bg-market-up" />
        <div style={{ flex: (data.breadth_yellow || 0) }} className="bg-market-ref" />
        <div style={{ flex: (data.breadth_floor || 0) + (data.breadth_red || 1) /* 1 to prevent 0 division on empty */}} className="bg-market-down" />
      </div>
      <div className="flex justify-between text-[10px] text-gray-400 mt-1.5 font-medium px-1">
        <span className="text-market-up">{(data.breadth_ceiling || 0) + (data.breadth_green || 0)} Up</span>
        <span className="text-market-ref">{data.breadth_yellow} Ref</span>
        <span className="text-market-down">{(data.breadth_floor || 0) + (data.breadth_red || 0)} Down</span>
      </div>
    </div>
  );
}
