import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { LanguageToggle } from './LanguageToggle'

describe('LanguageToggle component', () => {
  it('renders "EN" when language is "en"', () => {
    const { unmount } = render(<LanguageToggle lang="en" />)
    expect(screen.getByText('EN')).toBeInTheDocument()
    unmount()
  })

  it('renders "VI" when language is "vi"', () => {
    const { unmount } = render(<LanguageToggle lang="vi" />)
    expect(screen.getByText('VI')).toBeInTheDocument()
    unmount()
  })

  it('triggers onLanguageChange when clicked', () => {
    const handleLangChange = vi.fn()
    const { unmount } = render(<LanguageToggle lang="en" onLanguageChange={handleLangChange} />)

    const btn = screen.getByRole('button', { name: 'Switch to English' })
    fireEvent.click(btn)

    expect(handleLangChange).toHaveBeenCalledWith('vi')
    unmount()
  })
})
