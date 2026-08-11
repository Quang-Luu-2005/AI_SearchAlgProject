import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'

export function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  const saved = localStorage.getItem('floodroute_theme') as Theme | null
  if (saved === 'dark' || saved === 'light') return saved
  if (typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return 'light'
}

export type ThemeToggleProps = {
  theme?: Theme
  onThemeChange?: (theme: Theme) => void
}

export function ThemeToggle({ theme: externalTheme, onThemeChange }: ThemeToggleProps) {
  const [internalTheme, setInternalTheme] = useState<Theme>(getInitialTheme)
  const theme = externalTheme ?? internalTheme

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('floodroute_theme', theme)
  }, [theme])

  function toggleTheme() {
    const nextTheme = theme === 'light' ? 'dark' : 'light'
    if (!externalTheme) setInternalTheme(nextTheme)
    onThemeChange?.(nextTheme)
  }

  return (
    <button
      type="button"
      className="theme-toggle-btn"
      onClick={toggleTheme}
      title={theme === 'dark' ? 'Chuyển sang Chế độ Sáng (Light Mode)' : 'Chuyển sang Chế độ Tối (Dark Mode)'}
      aria-label={theme === 'dark' ? 'Chuyển sang Chế độ Sáng' : 'Chuyển sang Chế độ Tối'}
    >
      <span className="theme-toggle-icon" aria-hidden="true">
        {theme === 'dark' ? '🌙' : '☀️'}
      </span>
      <span className="theme-toggle-text">{theme === 'dark' ? 'Chế độ Tối' : 'Chế độ Sáng'}</span>
    </button>
  )
}
