import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import LoginScreen from './screens/Auth/LoginScreen';
import HomeScreen from './screens/Dashboard/HomeScreen';
import ProductsListScreen from './screens/Products/ListScreen';
import AlertsScreen from './screens/Alerts/AlertsScreen';
import ShoppingListScreen from './screens/Shopping/ShoppingListScreen';
import SettingsScreen from './screens/Settings/SettingsScreen';
import { useAuthStore } from './store/auth.store';

export type RootStackParamList = {
  Auth: undefined;
  App: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();

function AppTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Products" component={ProductsListScreen} />
      <Tab.Screen name="Alerts" component={AlertsScreen} />
      <Tab.Screen name="Shopping" component={ShoppingListScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const token = useAuthStore((s) => s.token);
  const isLogged = Boolean(token);
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isLogged ? (
        <Stack.Screen name="App" component={AppTabs} />
      ) : (
        <Stack.Screen name="Auth" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}
