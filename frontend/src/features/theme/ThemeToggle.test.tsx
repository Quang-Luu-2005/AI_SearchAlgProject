import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeToggle } from './ThemeToggle'

describe('ThemeToggle component', () => {
  it('renders correctly with light mode initial state', () => {
    const { unmount } = render(<ThemeToggle theme="light" />)
    expect(screen.getByText('Chế độ Sáng')).toBeInTheDocument()
    expect(screen.getByText('☀️')).toBeInTheDocument()
    unmount()
  })

  it('renders correctly with dark mode initial state', () => {
    const { unmount } = render(<ThemeToggle theme="dark" />)
    expect(screen.getByText('Chế độ Tối')).toBeInTheDocument()
    expect(screen.getByText('🌙')).toBeInTheDocument()
    unmount()
  })

  it('triggers onThemeChange when clicked', () => {
    const handleThemeChange = vi.fn()
    const { unmount } = render(<ThemeToggle theme="light" onThemeChange={handleThemeChange} />)

    const btn = screen.getByRole('button', { name: 'Chuyển sang Chế độ Tối' })
    fireEvent.click(btn)

    expect(handleThemeChange).toHaveBeenCalledWith('dark')
    unmount()
  })
})
