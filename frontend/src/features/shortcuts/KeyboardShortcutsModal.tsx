export type KeyboardShortcutsModalProps = {
  isOpen: boolean
  onClose: () => void
}

export function KeyboardShortcutsModal({ isOpen, onClose }: KeyboardShortcutsModalProps) {
  if (!isOpen) return null

  return (
    <div className="shortcuts-modal-overlay" role="dialog" aria-label="Danh sách phím tắt hệ thống" onClick={onClose}>
      <div className="shortcuts-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>⌨️ Danh sách Phím tắt Hệ thống</h3>
          <button type="button" className="close-modal-btn" onClick={onClose} aria-label="Đóng cửa sổ phím tắt">
            ×
          </button>
        </div>

        <div className="shortcuts-list">
          <div className="shortcut-row">
            <kbd className="key-cap">Space</kbd>
            <span>Bật / Tạm dừng phát Trace Player (Play / Pause)</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">←</kbd>
            <span>Tua lùi 1 bước trong mảng Trace Events (Previous Step)</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">→</kbd>
            <span>Tua tiến 1 bước trong mảng Trace Events (Next Step)</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">Ctrl + R / Cmd + R</kbd>
            <span>Nạp lại dữ liệu Graph & Reset lựa chọn</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">Esc</kbd>
            <span>Hủy chế độ chọn điểm trên bản đồ / Đóng cửa sổ trợ giúp</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">?</kbd>
            <span>Mở / Đóng bảng trợ giúp phím tắt</span>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-done" onClick={onClose}>
            Đã hiểu
          </button>
        </div>
      </div>
    </div>
  )
}
