import React from 'react';
import { View, Text, Pressable } from 'react-native';
import StatusBadge from './StatusBadge';
import { computeStatus } from '../utils/status';

export type Product = {
  id: string;
  name: string;
  location: 'fridge'|'freezer'|'pantry';
  quantity: number;
  daysToExpire: number | null;
};

export default function ProductCard({ item, onPress }: { item: Product; onPress?: () => void }) {
  const status = computeStatus(item.daysToExpire, item.quantity);
  return (
    <Pressable onPress={onPress} style={{ padding: 12, borderRadius: 12, backgroundColor: '#fff', marginBottom: 10, elevation: 1 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text style={{ fontSize: 16, fontWeight: '600' }}>{item.name}</Text>
        <StatusBadge status={status} />
      </View>
      <Text style={{ color: '#555', marginTop: 6 }}>{item.location} • qty: {item.quantity}</Text>
      {item.daysToExpire !== null && <Text style={{ color: '#777', marginTop: 4 }}>Jours restants: {item.daysToExpire}</Text>}
    </Pressable>
  );
}
