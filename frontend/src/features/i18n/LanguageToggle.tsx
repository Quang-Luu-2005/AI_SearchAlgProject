import { useEffect, useState } from 'react'
import { getInitialLanguage, type Language } from '../../lib/i18n'

export type LanguageToggleProps = {
  lang?: Language
  onLanguageChange?: (lang: Language) => void
}

export function LanguageToggle({ lang: externalLang, onLanguageChange }: LanguageToggleProps) {
  const [internalLang, setInternalLang] = useState<Language>(getInitialLanguage)
  const lang = externalLang ?? internalLang

  useEffect(() => {
    localStorage.setItem('floodroute_lang', lang)
    document.documentElement.setAttribute('lang', lang)
  }, [lang])

  function toggleLanguage() {
    const nextLang: Language = lang === 'en' ? 'vi' : 'en'
    if (!externalLang) setInternalLang(nextLang)
    onLanguageChange?.(nextLang)
  }

  return (
    <button
      type="button"
      className="lang-toggle-btn"
      onClick={toggleLanguage}
      title={lang === 'en' ? 'Chuyển sang Tiếng Việt' : 'Switch to English'}
      aria-label={lang === 'en' ? 'Switch to English' : 'Chuyển sang Tiếng Việt'}
    >
      <span className="lang-toggle-icon" aria-hidden="true">🌐</span>
      <span className="lang-toggle-text">{lang === 'en' ? 'EN' : 'VI'}</span>
    </button>
  )
}
