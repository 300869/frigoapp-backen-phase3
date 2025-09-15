import React from 'react';
import { Text, View } from 'react-native';
import { getStatusColor } from '../theme/colors';
import { Status } from '../utils/status';

export default function StatusBadge({ status }: { status: Status }) {
  const color = getStatusColor(status);
  return (
    <View style={{ paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8, backgroundColor: color.bg }}>
      <Text style={{ color: color.fg, fontWeight: '600' }}>{status}</Text>
    </View>
  );
}
