import React from 'react';
import { View, Text, FlatList } from 'react-native';
import { useTranslation } from 'react-i18next';
import ProductCard, { Product } from '../../components/ProductCard';

const MOCK: Product[] = [
  { id: '1', name: 'Yaourt', location: 'fridge', quantity: 2, daysToExpire: 2 },
  { id: '2', name: 'Poulet', location: 'freezer', quantity: 0, daysToExpire: null },
  { id: '3', name: 'Pain', location: 'pantry', quantity: 1, daysToExpire: -1 },
];

export default function HomeScreen() {
  const { t } = useTranslation();
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: '700', marginBottom: 12 }}>{t('home.title')}</Text>
      <FlatList
        data={MOCK}
        keyExtractor={(x) => x.id}
        renderItem={({ item }) => <ProductCard item={item} />}
        initialNumToRender={6}
        windowSize={7}
        removeClippedSubviews
      />
    </View>
  );
}
