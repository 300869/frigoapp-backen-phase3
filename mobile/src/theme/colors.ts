import { Status } from '../utils/status';

export function getStatusColor(status: Status) {
  switch (status) {
    case 'OUT_OF_STOCK':
      return { bg: '#E0E0E0', fg: '#333' };
    case 'EXPIRED':
      return { bg: '#FDE7E9', fg: '#B00020' };
    case 'SOON':
      return { bg: '#FFF2CC', fg: '#7A5D00' };
    case 'OK':
    default:
      return { bg: '#E8F5E9', fg: '#1B5E20' };
  }
}
