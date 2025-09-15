import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';
import fr from './locales/fr.json';
import en from './locales/en.json';
import es from './locales/es.json';

const resources = { fr: { translation: fr }, en: { translation: en }, es: { translation: es } };

function getDeviceLanguage() {
  try {
    const code = (Localization as any)?.getLocales?.()[0]?.languageCode;
    if (code) return code;
  } catch {}
  const anyLoc: any = Localization as any;
  if (anyLoc?.locale) return String(anyLoc.locale).split('-')[0];
  return 'fr';
}

if (!i18n.isInitialized) {
  i18n
    .use(initReactI18next)
    .init({
      compatibilityJSON: 'v3',
      resources,
      lng: getDeviceLanguage(),
      fallbackLng: 'fr',
      interpolation: { escapeValue: false },
    });
}

export default i18n;
