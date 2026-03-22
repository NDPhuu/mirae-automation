"use client";

import { useTopImpact } from "@/hooks/useMarketData";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorCard } from "@/components/ui/error-card";

export default function TopImpactList() {
  const { data, isLoading, error, mutate } = useTopImpact();

  if (error) return <ErrorCard message="Failed to load Top Impact" onRetry={mutate} />;

  if (isLoading || !data) return (
    <div className="bg-panel border border-zinc-800 rounded-lg shadow-md p-4 h-full flex flex-col gap-3">
      <Skeleton className="h-6 w-1/3 mb-2" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  );

  const maxPos = Math.max(...data.positive.map(i => Math.abs(i.impact_value)), 0.01);
  const maxNeg = Math.max(...data.negative.map(i => Math.abs(i.impact_value)), 0.01);

  return (
    <div className="bg-panel border border-zinc-800 rounded-lg shadow-md flex flex-col h-full">
      <div className="p-4 border-b border-zinc-800 flex justify-between items-center">
        <h3 className="font-bold text-zinc-100">Top tác động VN-Index</h3>
        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Đơn vị: Điểm</span>
      </div>

      <div className="grid grid-cols-2 divide-x divide-zinc-800 flex-1 p-2">
        {/* Positive Impact */}
        <div className="pr-2 space-y-1">
          <div className="text-[10px] font-bold text-market-up mb-2 px-2 uppercase tracking-wider opacity-80 italic">Tích cực</div>
          {data.positive.map((item) => (
            <div key={item.symbol} className="relative flex items-center justify-between px-2 py-1.5 hover:bg-zinc-800/80 rounded transition-colors group overflow-hidden">
              {/* Background Progress Bar */}
              <div
                className="absolute inset-y-0 left-0 bg-market-up/10 -z-0 transition-all duration-500"
                style={{ width: `${(Math.abs(item.impact_value) / maxPos) * 100}%` }}
              />
              <div className="flex flex-col z-10">
                <span className="text-sm font-bold text-zinc-200">{item.symbol}</span>
                <span className="text-[10px] text-zinc-500 leading-none">Giá: {(item.price * 1000).toLocaleString()}</span>
              </div>
              <div className="text-right z-10">
                <div className="text-sm font-black text-market-up">{item.impact_value.toFixed(2)}</div>
                <div className="text-[10px] text-zinc-400 group-hover:text-market-up transition-colors font-medium">+{item.change_percent.toFixed(2)}%</div>
              </div>
            </div>
          ))}
        </div>

        {/* Negative Impact */}
        <div className="pl-2 space-y-1">
          <div className="text-[10px] font-bold text-market-down mb-2 px-2 uppercase tracking-wider opacity-80 italic">Tiêu cực</div>
          {data.negative.map((item) => (
            <div key={item.symbol} className="relative flex items-center justify-between px-2 py-1.5 hover:bg-zinc-800/80 rounded transition-colors group overflow-hidden">
              {/* Background Progress Bar (Right Aligned) */}
              <div
                className="absolute inset-y-0 right-0 bg-market-down/10 -z-0 transition-all duration-500"
                style={{ width: `${(Math.abs(item.impact_value) / maxNeg) * 100}%` }}
              />
              <div className="flex flex-col z-10">
                <span className="text-sm font-bold text-zinc-200">{item.symbol}</span>
                <span className="text-[10px] text-zinc-500 leading-none">Giá: {(item.price * 1000).toLocaleString()}</span>
              </div>
              <div className="text-right z-10">
                <div className="text-sm font-black text-market-down">{item.impact_value.toFixed(2)}</div>
                <div className="text-[10px] text-zinc-400 group-hover:text-market-down transition-colors font-medium">{item.change_percent.toFixed(2)}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
