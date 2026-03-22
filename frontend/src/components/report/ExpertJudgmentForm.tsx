"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import useSWR from "swr";
import api from "@/lib/api";

const fetcher = (url: string) => api.get(url).then(res => res.data);

export interface JudgmentData {
  pe_ratio: number;
  technical_score: number;
  technical_rating: string;
  liquidity_comment: string;
  expert_comment: string;
}

interface ExpertJudgmentFormProps {
  onSubmit: (data: JudgmentData) => void;
  isGenerating: boolean;
}

const LIQUIDITY_OPTIONS = [
  "Thanh khoản bùng nổ, dòng tiền vào mạnh",
  "Thanh khoản duy trì ở mức trung bình",
  "Thanh khoản sụt giảm, bên mua thận trọng",
  "Tùy chỉnh..."
];

export default function ExpertJudgmentForm({ onSubmit, isGenerating }: ExpertJudgmentFormProps) {
  const { data: systemStatus } = useSWR('/system/status', fetcher, {
    refreshInterval: 3000
  });

  const isSyncing = systemStatus?.state === "SYNCING";
  const syncMessage = systemStatus?.message || "Đang đồng bộ dữ liệu tĩnh...";

  const [isCustomLiquidity, setIsCustomLiquidity] = useState(false);
  const [formData, setFormData] = useState<JudgmentData>({
    pe_ratio: 14.5,
    technical_score: 5,
    technical_rating: "Tích cực",
    liquidity_comment: LIQUIDITY_OPTIONS[1],
    expert_comment: "Thị trường phân hóa, khối ngoại bán ròng chờ tín hiệu từ vĩ mô.",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleLiquidityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (val === "Tùy chỉnh...") {
      setIsCustomLiquidity(true);
      setFormData({ ...formData, liquidity_comment: "" });
    } else {
      setIsCustomLiquidity(false);
      setFormData({ ...formData, liquidity_comment: val });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-panel border border-zinc-800 rounded-lg shadow-md p-5 flex flex-col gap-5 h-full">
      <div>
        <h3 className="font-bold text-lg text-zinc-100 mb-1">Điều chỉnh của Analyst</h3>
        <p className="text-[11px] text-zinc-500 uppercase tracking-widest font-semibold">Đưa ngữ cảnh vào hệ thống AI.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <label className="flex flex-col gap-1.5 text-xs font-bold text-zinc-400">
          P/E Ratio (VN-Index)
          <input
            type="number" step="0.1"
            value={formData.pe_ratio}
            onChange={(e) => setFormData({ ...formData, pe_ratio: parseFloat(e.target.value) })}
            className="p-2 text-sm bg-zinc-900 border border-zinc-800 text-zinc-200 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all shadow-inner"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-zinc-400">
          Điểm số kỹ thuật (-7 đến +7)
          <input
            type="number" min="-7" max="7"
            value={formData.technical_score}
            onChange={(e) => {
              const score = parseInt(e.target.value) || 0;
              let rating = "Trung tính";
              if (score >= 4) rating = "Tích cực";
              else if (score <= -4) rating = "Tiêu cực";

              setFormData({ ...formData, technical_score: score, technical_rating: rating });
            }}
            className="p-2 text-sm bg-zinc-900 border border-zinc-800 text-zinc-200 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all shadow-inner"
          />
        </label>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <label className="flex flex-col gap-1.5 text-xs font-bold text-zinc-400">
          Trạng thái kỹ thuật
          <select
            value={formData.technical_rating}
            onChange={(e) => setFormData({ ...formData, technical_rating: e.target.value })}
            className="p-2 text-sm bg-zinc-900 border border-zinc-800 text-zinc-200 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all shadow-inner"
          >
            <option>Tiêu cực</option>
            <option>Trung tính</option>
            <option>Tích cực</option>
          </select>
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-zinc-400">
          Nhận xét về thanh khoản (Optional)
          {!isCustomLiquidity ? (
            <select
              value={formData.liquidity_comment}
              onChange={handleLiquidityChange}
              className="p-2 text-sm bg-zinc-900 border border-zinc-800 text-zinc-200 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all shadow-inner"
            >
              {LIQUIDITY_OPTIONS.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
          ) : (
            <div className="flex bg-zinc-900 border border-zinc-800 rounded focus-within:ring-2 focus-within:ring-blue-600 transition-all shadow-inner overflow-hidden">
              <input
                type="text"
                autoFocus
                placeholder="Nhập thanh khoản..."
                value={formData.liquidity_comment}
                onChange={(e) => setFormData({ ...formData, liquidity_comment: e.target.value })}
                className="p-2 text-sm w-full bg-transparent text-zinc-200 outline-none"
              />
              <button
                type="button"
                onClick={() => setIsCustomLiquidity(false)}
                className="px-2 text-[10px] bg-zinc-800 hover:bg-zinc-700 text-zinc-400 uppercase font-bold transition-colors"
              >
                Hủy
              </button>
            </div>
          )}
        </label>
      </div>

      <label className="flex flex-col gap-1.5 text-xs font-bold text-zinc-400">
        Nhận xét của Analyst
        <textarea
          rows={3}
          value={formData.expert_comment}
          onChange={(e) => setFormData({ ...formData, expert_comment: e.target.value })}
          className="p-2 text-sm bg-zinc-900 border border-zinc-800 text-zinc-200 rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all shadow-inner resize-none"
        />
      </label>

      <div className="flex-1" /> {/* Spacer */}

      <button
        type="submit"
        disabled={isGenerating || isSyncing}
        className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-4 rounded transition-all disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 shadow-lg hover:shadow-orange-900/40"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Đang tổng hợp AI...
          </>
        ) : isSyncing ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {syncMessage}
          </>
        ) : (
          "Bắt đầu tạo báo cáo AI"
        )}
      </button>
    </form>
  );
}
