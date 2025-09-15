import dayjs from 'dayjs';

export function daysBetween(a: string, b: string) {
  return dayjs(b).diff(dayjs(a), 'day');
}
