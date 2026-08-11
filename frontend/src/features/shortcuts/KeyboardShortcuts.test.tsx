import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { KeyboardShortcutsModal } from './KeyboardShortcutsModal'

describe('KeyboardShortcutsModal component', () => {
  it('renders modal content when open', () => {
    const { unmount } = render(<KeyboardShortcutsModal isOpen={true} onClose={vi.fn()} />)
    expect(screen.getByText('⌨️ Danh sách Phím tắt Hệ thống')).toBeInTheDocument()
    expect(screen.getByText('Space')).toBeInTheDocument()
    expect(screen.getByText('Bật / Tạm dừng phát Trace Player (Play / Pause)')).toBeInTheDocument()
    unmount()
  })

  it('triggers onClose when close button is clicked', () => {
    const handleClose = vi.fn()
    const { unmount } = render(<KeyboardShortcutsModal isOpen={true} onClose={handleClose} />)

    fireEvent.click(screen.getByRole('button', { name: 'Đóng cửa sổ phím tắt' }))
    expect(handleClose).toHaveBeenCalledTimes(1)
    unmount()
  })
})
