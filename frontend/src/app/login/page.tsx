'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'analyst' | 'admin'>('analyst');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (role === 'admin') {
      const adminPass = process.env.NEXT_PUBLIC_ADMIN_PASSWORD || 'admin123';
      if (password === adminPass) {
        document.cookie = "user_role=admin; path=/; max-age=86400; SameSite=Lax";
        localStorage.setItem('user_role', 'admin');
        router.push('/admin');
      } else {
        setError('Mật khẩu Admin không chính xác');
      }
    } else {
      document.cookie = "user_role=analyst; path=/; max-age=86400; SameSite=Lax";
      localStorage.setItem('user_role', 'analyst');
      router.push('/');
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center overflow-hidden bg-black">
      {/* Background Animated Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-brand/20 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-zinc-500/10 rounded-full blur-[120px] animate-pulse delay-1000" />
      
      {/* Glassmorphism Card */}
      <div className="relative z-10 w-full max-w-md p-8 border border-glass-border bg-glass backdrop-blur-glass rounded-2xl shadow-glass">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-brand to-zinc-500 bg-clip-text text-transparent">
            Mirae Asset
          </h1>
          <p className="text-zinc-500 mt-2 font-medium">Hệ thống Tự động hóa Analyst</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="flex p-1 bg-white/5 rounded-lg border border-white/5">
            <button
              type="button"
              onClick={() => setRole('analyst')}
              className={`flex-1 py-2 px-4 rounded-md transition-all text-sm font-medium ${
                role === 'analyst' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Analyst
            </button>
            <button
              type="button"
              onClick={() => setRole('admin')}
              className={`flex-1 py-2 px-4 rounded-md transition-all text-sm font-medium ${
                role === 'admin' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Admin
            </button>
          </div>

          {role === 'admin' && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-400">Mật khẩu Quản trị</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand/50 text-white placeholder-zinc-600 transition-all"
                placeholder="••••••••"
                required
              />
            </div>
          )}

          {error && <p className="text-market-down text-sm text-center font-medium">{error}</p>}

          <button
            type="submit"
            className="w-full py-3 px-4 bg-gradient-to-r from-brand to-orange-700 hover:from-brand-hover hover:to-brand text-black font-bold rounded-xl transition-all active:scale-[0.98] shadow-[0_0_25px_rgba(249,115,22,0.3)]"
          >
            {role === 'admin' ? 'ĐĂNG NHẬP QUẢN TRỊ' : 'VÀO DASHBOARD ANALYST'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-white/5 text-center">
          <p className="text-xs text-zinc-600 uppercase tracking-widest font-medium">
            Mirae Asset Securities (Vietnam)
          </p>
        </div>
      </div>
    </div>
  );
}
