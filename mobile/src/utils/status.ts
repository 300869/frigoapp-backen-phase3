export type Status = 'OK' | 'SOON' | 'EXPIRED' | 'OUT_OF_STOCK';

export function computeStatus(daysToExpire: number | null, qty: number): Status {
  if (qty <= 0) return 'OUT_OF_STOCK';
  if (daysToExpire === null) return 'OK';
  if (daysToExpire < 0) return 'EXPIRED';
  if (daysToExpire <= 3) return 'SOON';
  return 'OK';
}
