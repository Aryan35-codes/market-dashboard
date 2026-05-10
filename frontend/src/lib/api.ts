const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/market";

export async function fetchMarketData<T>(
  endpoint: string,
  revalidate: number = 15
): Promise<{ status: string; data: T | null; cache_age_seconds: number | null }> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      next: { revalidate },
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  } catch {
    return { status: "error", data: null, cache_age_seconds: null };
  }
}

export function formatTimeAgo(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return "";
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${Math.round(seconds)}s ago`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ago`;
  return `${Math.round(seconds / 3600)}h ago`;
}

export function formatNumber(num: number): string {
  if (Math.abs(num) >= 10000000) return `${(num / 10000000).toFixed(2)}Cr`;
  if (Math.abs(num) >= 100000) return `${(num / 100000).toFixed(2)}L`;
  if (Math.abs(num) >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toFixed(2);
}

export function formatPrice(price: number): string {
  return price.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
