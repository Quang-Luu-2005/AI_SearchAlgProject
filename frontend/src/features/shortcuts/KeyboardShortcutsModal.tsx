import { t, type Language } from '../../lib/i18n'

export type KeyboardShortcutsModalProps = {
  isOpen: boolean
  onClose: () => void
  lang?: Language
}

export function KeyboardShortcutsModal({ isOpen, onClose, lang = 'en' }: KeyboardShortcutsModalProps) {
  if (!isOpen) return null

  return (
    <div className="shortcuts-modal-overlay" role="dialog" aria-label={t('shortcuts_modal_title', lang)} onClick={onClose}>
      <div className="shortcuts-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('shortcuts_modal_title', lang)}</h3>
          <button type="button" className="close-modal-btn" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="shortcuts-list">
          <div className="shortcut-row">
            <kbd className="key-cap">Space</kbd>
            <span>{t('shortcut_space', lang)}</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">←</kbd>
            <span>{t('shortcut_prev', lang)}</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">→</kbd>
            <span>{t('shortcut_next', lang)}</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">Ctrl + R / Cmd + R</kbd>
            <span>{t('shortcut_reload', lang)}</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">Esc</kbd>
            <span>{t('shortcut_esc', lang)}</span>
          </div>

          <div className="shortcut-row">
            <kbd className="key-cap">?</kbd>
            <span>{t('shortcut_help', lang)}</span>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-done" onClick={onClose}>
            {t('done', lang)}
          </button>
        </div>
      </div>
    </div>
  )
}
