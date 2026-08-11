import { describe, expect, it } from 'vitest'
import { t, getInitialLanguage } from './i18n'

describe('i18n module', () => {
  it('returns "en" as default initial language', () => {
    expect(getInitialLanguage()).toBe('en')
  })

  it('translates keys correctly into English', () => {
    expect(t('clear_results', 'en')).toBe('Clear Results')
    expect(t('run_algorithm', 'en')).toBe('Run Algorithm')
    expect(t('panel_title', 'en')).toBe('Control Panel')
  })

  it('translates keys correctly into Vietnamese', () => {
    expect(t('clear_results', 'vi')).toBe('Xóa kết quả')
    expect(t('run_algorithm', 'vi')).toBe('Chạy thuật toán')
    expect(t('panel_title', 'vi')).toBe('Bảng điều khiển')
  })

  it('interpolates parameters correctly', () => {
    expect(t('stops_needed', 'en', { count: 3 })).toBe('Need to select 3 more stop(s) (minimum 5 delivery stops).')
    expect(t('stops_needed', 'vi', { count: 3 })).toBe('Cần chọn thêm 3 điểm nữa (tối thiểu 5 điểm giao hàng).')
  })
})
