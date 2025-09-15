# FreshKeeper - Phase 7 Starter (Expo + TypeScript)

## 1) Create the Expo app
```
npx create-expo-app freshkeeper-app --template blank@latest
cd freshkeeper-app
```

## 2) Install deps (from INSIDE the project folder)
> PowerShell: put everything on ONE line.
```
npm i @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs react-native-gesture-handler react-native-safe-area-context react-native-screens i18next react-i18next zustand axios expo-localization
npm i -D typescript @types/react @types/react-native
```
If Expo asks to align versions:
```
npx expo install react-native
```

## 3) Copy files
Copy `App.tsx`, the whole `src/`, `.env.example`, and `tsconfig.json` into your Expo project root.

## 4) .env
Create `.env` based on `.env.example` and set:
```
EXPO_PUBLIC_API_BASE_URL=http://192.168.X.X:8000
```

## 5) Start
```
npx expo start
```

## Notes
- Login is mocked. Wire to `/auth/token` later.
- i18n files: `src/i18n/locales/*`
- Status colors: `src/theme/colors.ts`
- API client with Bearer: `src/api/client.ts`
