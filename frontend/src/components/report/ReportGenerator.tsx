"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Copy, FileText, Check, Bot } from "lucide-react";
import ExpertJudgmentForm, { JudgmentData } from "./ExpertJudgmentForm";
import api from "@/lib/api";

// Helper to strip markdown for Zalo pasting
const stripMarkdown = (md: string) => {
  return md
    .replace(/\*\*(.*?)\*\*/g, "$1") // bold
    .replace(/\*(.*?)\*/g, "$1")     // italic
    .replace(/__(.*?)__/g, "$1")     // bold
    .replace(/_(.*?)_/g, "$1")       // italic
    .replace(/#(.*?)\n/g, "$1\n")    // headers
    .replace(/\[(.*?)\]\(.*?\)/g, "$1") // links
    .replace(/`(.*?)`/g, "$1");      // inline code
};

export default function ReportGenerator() {
  const [reportMarkdown, setReportMarkdown] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleCopy = () => {
    if (!reportMarkdown) return;
    const cleanText = stripMarkdown(reportMarkdown);
    navigator.clipboard.writeText(cleanText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleExportWord = () => {
    if (!reportMarkdown) return;
    alert("Export to Word feature connects to Backend API /export-word (Coming soon).");
  };

  const handleGenerate = async (data: JudgmentData) => {
    setIsGenerating(true);
    setReportMarkdown(null); // clear previous to show loading state

    try {
      const response = await api.post("/report/generate", {
        manual_override: data,
      });
      setReportMarkdown(response.data.report_content);
    } catch (err) {
      console.error(err);
      alert("Failed to generate report");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1">
        <ExpertJudgmentForm onSubmit={handleGenerate} isGenerating={isGenerating} />
      </div>

      <div className="lg:col-span-2 flex flex-col h-full">
        {/* Output Toolbar */}
        <div className="bg-[#1a1a1a] border border-zinc-800 rounded-t-lg p-3 flex justify-between items-center shadow-md">
          <h3 className="font-bold text-zinc-100 flex items-center gap-2">
            Generated Report
            {reportMarkdown && <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>}
          </h3>

          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              disabled={!reportMarkdown || isGenerating}
              title="Copy straight to Zalo (No Markdown)"
              className="p-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 text-xs font-semibold"
            >
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied!" : "Copy"}
            </button>
            <button
              onClick={handleExportWord}
              disabled={!reportMarkdown || isGenerating}
              title="Export to Word (.docx)"
              className="p-1.5 bg-zinc-800 hover:bg-[#2b579a] text-zinc-300 hover:text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 text-xs font-semibold"
            >
              <FileText className="w-4 h-4" />
              Word
            </button>
          </div>
        </div>

        {/* Output Content Field */}
        <div className="bg-panel border border-t-0 border-zinc-800 rounded-b-lg p-8 flex-1 min-h-[400px] shadow-md overflow-y-auto relative">

          {isGenerating && (
            <div className="absolute inset-0 z-10 bg-panel/80 backdrop-blur-sm flex flex-col items-center justify-center animate-in fade-in duration-300 rounded-b-lg">
              <div className="relative flex items-center justify-center mb-4">
                <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full"></div>
                <Bot className="w-12 h-12 text-blue-400 animate-bounce relative z-10" />
              </div>
              <h3 className="text-zinc-200 font-bold text-lg">AI đang tổng hợp và viết báo cáo...</h3>
              <p className="text-zinc-500 text-sm mt-1">(Vui lòng đợi khoảng 5-10s)</p>
            </div>
          )}

          {reportMarkdown && !isGenerating ? (
            <article className="prose prose-invert prose-zinc max-w-none prose-p:leading-relaxed prose-headings:text-zinc-100 prose-a:text-blue-400">
              <ReactMarkdown>{reportMarkdown}</ReactMarkdown>
            </article>
          ) : !isGenerating && (
            <div className="h-full flex items-center justify-center text-zinc-300 italic">
              Đang chờ tạo… Hãy nhập đánh giá của Analyst để bắt đầu.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
