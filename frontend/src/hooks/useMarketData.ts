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

// Global Poll Interval
const REFRESH_INTERVAL = 5000;
const SWR_CONFIG = {
  refreshInterval: REFRESH_INTERVAL,
  keepPreviousData: true, 
  revalidateOnFocus: true,
};

export function useMarketOverview() {
  const { data, error, isLoading, mutate } = useSWR<MarketOverview>('/overview', fetcher, SWR_CONFIG);
  return { data, error, isLoading, mutate };
}

export function useTopImpact() {
  const { data, error, isLoading, mutate } = useSWR<TopImpactData>('/top-impact?limit=10', fetcher, SWR_CONFIG);
  return { data, error, isLoading, mutate };
}

export function useSectorPerformance() {
  const { data, error, isLoading, mutate } = useSWR<SectorPerformanceData>('/sector-performance', fetcher, SWR_CONFIG);
  return { data, error, isLoading, mutate };
}

export function useForeignTrading() {
  const { data, error, isLoading, mutate } = useSWR<ForeignTradingData>('/foreign-trading?limit=10', fetcher, SWR_CONFIG);
  return { data, error, isLoading, mutate };
}
