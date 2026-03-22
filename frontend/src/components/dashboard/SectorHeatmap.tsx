"use client";

import { useSectorPerformance } from "@/hooks/useMarketData";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorCard } from "@/components/ui/error-card";

export default function SectorHeatmap() {
  const { data, isLoading, error, mutate } = useSectorPerformance();

  if (error) return <ErrorCard message="Failed to load Sector Performance" onRetry={mutate} />;

  if (isLoading || !data) return (
    <div className="bg-panel border border-zinc-800 rounded-lg shadow-md p-4 h-full flex flex-col gap-4">
      <Skeleton className="h-6 w-1/4" />
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {[...Array(12)].map((_, i) => (
          <Skeleton key={i} className="aspect-video w-full rounded-md" />
        ))}
      </div>
    </div>
  );

  // Sorting strictly by avg_change visually helps the heatmap
  const sortedSectors = [...data.sectors].sort((a, b) => b.avg_change - a.avg_change);

  const getHeatmapColor = (change: number) => {
    if (change >= 2.0) return "bg-[#00d26a] text-zinc-950"; // Bright Green, dark text
    if (change >= 0.5) return "bg-[#00d26a]/70 text-zinc-50";
    if (change > 0) return "bg-[#00d26a]/30 text-zinc-100 border border-[#00d26a]/20";
    if (change === 0) return "bg-[#f7ca49]/30 text-[#f7ca49] border border-[#f7ca49]/20";
    if (change <= -2.0) return "bg-[#fc5757] text-white"; // Bright Red, white text
    if (change <= -0.5) return "bg-[#fc5757]/80 text-white";
    return "bg-[#fc5757]/30 text-red-100 border border-[#fc5757]/20";
  };

  return (
    <div className="bg-panel border border-zinc-800 rounded-lg shadow-md flex flex-col h-full">
      <div className="p-4 border-b border-zinc-800 flex justify-between items-center">
        <h3 className="font-bold text-zinc-100">Diễn biến nhóm ngành</h3>
        <span className="text-[10px] text-zinc-500 uppercase font-semibold">Real-time Avg %</span>
      </div>
      <div className="p-4 flex-1 overflow-y-auto">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {sortedSectors.map((s) => (
            <div
              key={s.sector}
              className={`p-3 rounded-md flex flex-col justify-between aspect-[3/2] transition-transform duration-200 cursor-pointer hover:scale-[1.03] shadow-inner ${getHeatmapColor(s.avg_change)}`}
            >
              <div className="text-[11px] font-bold leading-tight mix-blend-normal opacity-90">{s.sector}</div>
              <div className="flex items-end justify-between mt-2">
                <span className="text-xl font-black tracking-tighter mix-blend-normal">
                  {s.avg_change > 0 ? '+' : ''}{s.avg_change.toFixed(2)}%
                </span>
                <div className="text-[9px] font-bold opacity-70 truncate max-w-[60px] text-right">
                  {s.top_symbols}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
