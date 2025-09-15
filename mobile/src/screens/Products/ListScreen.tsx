import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { View, Text, FlatList, RefreshControl, TextInput } from 'react-native';
import ProductCard from '../../components/ProductCard';
import { listProducts, ProductDto } from '../../api/products';

export default function ProductsListScreen() {
  const [items, setItems] = useState<ProductDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listProducts({ page: 1, size: 50, search });
      setItems(data);
    } catch (e) {
      // fallback mock si API down
      setItems([
        { id: '1', name: 'Yaourt', location: 'fridge', quantity: 2, days_to_expire: 2 },
        { id: '2', name: 'Poulet', location: 'freezer', quantity: 0, days_to_expire: null },
      ]);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const renderItem = useCallback(({ item }: { item: ProductDto }) => (
    <ProductCard
      item={{
        id: String(item.id),
        name: item.name,
        location: item.location,
        quantity: item.quantity ?? 0,
        daysToExpire: (item as any).days_to_expire ?? null
      }}
    />
  ), []);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: '700', marginBottom: 12 }}>Produits</Text>
      <TextInput
        placeholder="Rechercher..."
        value={search}
        onChangeText={setSearch}
        style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 10, marginBottom: 12 }}
      />
      <FlatList
        data={items}
        keyExtractor={(x) => String(x.id)}
        renderItem={renderItem}
        initialNumToRender={12}
        windowSize={9}
        maxToRenderPerBatch={12}
        removeClippedSubviews
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={async () => {
            setRefreshing(true); await fetchData(); setRefreshing(false);
          }} />
        }
        ListEmptyComponent={!loading ? <Text style={{ textAlign: 'center', marginTop: 40, color: '#777' }}>Aucun produit</Text> : null}
      />
    </View>
  );
}
