"use client";

import { useForeignTrading } from "@/hooks/useMarketData";

export default function ForeignActivityPanel() {
  const { data, isLoading, error } = useForeignTrading();

  if (isLoading) return <div className="h-48 bg-panel animate-pulse rounded-lg border border-panel-border"></div>;
  if (error || !data) return <div className="h-48 bg-panel rounded-lg border border-panel-border flex items-center justify-center text-red-500">Failed to load data</div>;

  return (
    <div className="bg-panel border border-panel-border rounded-lg shadow-xl overflow-hidden flex flex-col">
      <div className="p-4 border-b border-panel-border bg-[#1a1a1a] flex justify-between items-center">
        <h3 className="font-bold text-gray-200">Foreign Activity (Net Value)</h3>
        {data.top_buy.length > 0 && (
          <span className="text-[10px] text-zinc-500 font-mono">Session: {data.top_buy[0].trading_date}</span>
        )}
      </div>
      
      <div className="flex-1 divide-y divide-panel-border">
        {/* Top Buy */}
        <div className="p-3">
          <div className="text-xs font-semibold text-market-up mb-2 uppercase tracking-tight">Top Buy</div>
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

        {/* Top Sell */}
        <div className="p-3">
          <div className="text-xs font-semibold text-market-down mb-2 uppercase tracking-tight">Top Sell</div>
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
