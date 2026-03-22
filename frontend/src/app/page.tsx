import MarketMetricsRow from "@/components/dashboard/MarketMetricsRow";
import TopImpactList from "@/components/dashboard/TopImpactList";
import SectorHeatmap from "@/components/dashboard/SectorHeatmap";
import ForeignActivityPanel from "@/components/dashboard/ForeignActivityPanel";
import ReportGenerator from "@/components/report/ReportGenerator";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-8 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <header className="flex flex-col gap-1 pb-4 border-b border-zinc-800">
        <h1 className="text-2xl font-bold tracking-tight text-zinc-100">Analyst Dashboard</h1>
        <p className="text-sm text-zinc-500">Professional financial terminal & AI insights generated in real-time.</p>
      </header>

      {/* Row 1: Top 4 Metrics */}
      <section>
        <MarketMetricsRow />
      </section>

      {/* Row 2: Detailed Data (30% Left, 40% Middle, 30% Right) */}
      <section className="grid grid-cols-1 lg:grid-cols-10 gap-6 h-full">
        <div className="lg:col-span-3">
          {/* Top Tác động (30%) */}
          <TopImpactList />
        </div>
        <div className="lg:col-span-4">
          {/* Nhóm ngành (40%) */}
          <SectorHeatmap />
        </div>
        <div className="lg:col-span-3">
          {/* Khối ngoại (30%) */}
          <ForeignActivityPanel />
        </div>
      </section>

      {/* Divider */}
      <div className="py-6">
        <div className="w-full h-px bg-zinc-800" />
      </div>

      {/* AI Report Generation Layer */}
      <section className="pb-16">
        <header className="mb-4">
          <h2 className="text-xl font-bold text-zinc-100">Daily Report Generator</h2>
          <p className="text-sm text-zinc-500">Cung cấp nhận định của Analyst để hệ thống tự động tạo nội dung báo cáo.</p>
        </header>

        <ReportGenerator />
      </section>

    </main>
  );
}
