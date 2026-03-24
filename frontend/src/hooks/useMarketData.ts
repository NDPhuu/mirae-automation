import useSWR from 'swr';
import api from '../lib/api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

// Define Types matching FastAPI schemas
export interface MarketOverview {
  symbol: string;
  trading_date: string;
  point: number | null;
  change_point: number | null;
  change_percent: number | null;
  total_volume: number | null;
  total_value: number | null;
  breadth_green: number | null;
  breadth_red: number | null;
  breadth_yellow: number | null;
  breadth_ceiling: number | null;
  breadth_floor: number | null;
}

export interface ImpactMetric {
  symbol: string;
  sector: string | null;
  price: number;
  ref_price: number;
  change_percent: number;
  impact_value: number;
}

export interface TopImpactData {
  positive: ImpactMetric[];
  negative: ImpactMetric[];
}

export interface SectorPerformanceMetric {
  trading_date: string;
  sector: string;
  avg_change: number;
  total_stocks: number;
  top_symbols?: string;
}

export interface SectorPerformanceData {
  sectors: SectorPerformanceMetric[];
}

export interface ForeignTradeMetric {
  symbol: string;
  trading_date: string;
  f_buy_val: number;
  f_sell_val: number;
  net_val: number;
}

export interface ForeignTradingData {
  top_buy: ForeignTradeMetric[];
  top_sell: ForeignTradeMetric[];
  total_net_val: number;
}

export interface SyncStatusData {
  id: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  type: 'INTRADAY' | 'EOD';
  processed: number;
  total: number;
  failed: number;
  eta_seconds: number;
}

// Vietnam Time (UTC+7) Utilities
export function getVNTime() {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  return new Date(utc + 3600000 * 7);
}

export function isMarketOpen() {
  const vnTime = getVNTime();
  const hours = vnTime.getHours();
  const minutes = vnTime.getMinutes();
  const day = vnTime.getDay(); // 0 is Sunday, 6 is Saturday

  const isWeekday = day >= 1 && day <= 5;
  const timeSeconds = hours * 3600 + minutes * 60;
  
  // HOSE/HNX Hours: 9:00 - 15:15 (buffered)
  const startSeconds = 9 * 3600;
  const endSeconds = 15 * 3600 + 15 * 60;

  return isWeekday && timeSeconds >= startSeconds && timeSeconds <= endSeconds;
}

// Global Poll Interval (Reduced for less API pressure)
const REFRESH_INTERVAL = 15000; // 15 seconds

export function usePollingControl() {
  const { data: isLive, mutate } = useSWR('live-mode', () => {
    return localStorage.getItem('live_mode') === 'true';
  }, { fallbackData: false });

  const toggleLive = () => {
    const newValue = !isLive;
    localStorage.setItem('live_mode', String(newValue));
    mutate(newValue);
  };

  return { isLive, toggleLive };
}

function getPollingInterval(baseInterval: number, isLive: boolean) {
  if (isLive) return baseInterval;
  return isMarketOpen() ? baseInterval : 0; // 0 disables SWR polling
}

export function useMarketOverview() {
  const { isLive } = usePollingControl();
  const { data, error, isLoading, mutate } = useSWR<MarketOverview>('/overview', fetcher, {
    refreshInterval: getPollingInterval(REFRESH_INTERVAL, !!isLive),
    keepPreviousData: true,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, mutate };
}

export function useTopImpact() {
  const { isLive } = usePollingControl();
  const { data, error, isLoading, mutate } = useSWR<TopImpactData>('/top-impact?limit=10', fetcher, {
    refreshInterval: getPollingInterval(REFRESH_INTERVAL, !!isLive),
    keepPreviousData: true,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, mutate };
}

export function useSectorPerformance() {
  const { isLive } = usePollingControl();
  const { data, error, isLoading, mutate } = useSWR<SectorPerformanceData>('/sector-performance', fetcher, {
    refreshInterval: getPollingInterval(REFRESH_INTERVAL, !!isLive),
    keepPreviousData: true,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, mutate };
}

export function useForeignTrading() {
  const { isLive } = usePollingControl();
  const { data, error, isLoading, mutate } = useSWR<ForeignTradingData>('/foreign-trading?limit=10', fetcher, {
    refreshInterval: getPollingInterval(REFRESH_INTERVAL, !!isLive),
    keepPreviousData: true,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, mutate };
}

export function useSyncStatus() {
  const { isLive } = usePollingControl();
  const { data, error, isLoading, mutate } = useSWR<SyncStatusData>('/sync-status', fetcher, {
    refreshInterval: (data) => {
      if (data?.status === 'running') return 2000;
      return getPollingInterval(30000, !!isLive);
    },
    keepPreviousData: true,
    revalidateOnFocus: false,
  });
  return { data, error, isLoading, mutate };
}
