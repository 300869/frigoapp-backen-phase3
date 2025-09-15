import React from "react";
import { SafeAreaView, StatusBar, View, Text } from "react-native";

export default function App() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#0f172a" }}>
      <StatusBar />
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <Text style={{ color: "white", fontSize: 22, fontWeight: "800" }}>
          App minimale OK
        </Text>
      </View>
    </SafeAreaView>
  );
}
