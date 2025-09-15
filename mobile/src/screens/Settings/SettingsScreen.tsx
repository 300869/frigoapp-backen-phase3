import React from 'react';
import { View, Text, Button } from 'react-native';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/auth.store';

export default function SettingsScreen() {
  const { t } = useTranslation();
  const logout = useAuthStore((s) => s.logout);

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>Settings</Text>
      <Button title={t('auth.logout')} onPress={logout} />
    </View>
  );
}
