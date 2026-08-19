import { describe, expect, it } from 'vitest'
import { t, getInitialLanguage, translateGraphLabel } from './i18n'

describe('i18n module', () => {
  it('returns "en" as default initial language', () => {
    expect(getInitialLanguage()).toBe('en')
  })

  it('translates keys correctly into English', () => {
    expect(t('clear_results', 'en')).toBe('Clear Results')
    expect(t('run_algorithm', 'en')).toBe('Run Algorithm')
    expect(t('panel_title', 'en')).toBe('Control Panel')
    expect(t('eyebrow_title', 'en')).toBe('Optimal path visualizer')
    expect(t('group_two_point', 'en')).toBe('🔍 Two-Point Search (Single Algorithm)')
    expect(t('group_multi_stop', 'en')).toBe('📦 Multi-Stop Tour (TSP)')
    expect(t('group_comparison', 'en')).toBe('📊 Algorithm Comparison')
    expect(t('tour_itinerary_title', 'en')).toBe('Delivery Stop Itinerary')
    expect(t('depot_badge', 'en')).toBe('Depot')
  })

  it('translates keys correctly into Vietnamese', () => {
    expect(t('clear_results', 'vi')).toBe('Xóa kết quả')
    expect(t('run_algorithm', 'vi')).toBe('Chạy thuật toán')
    expect(t('panel_title', 'vi')).toBe('Bảng điều khiển')
    expect(t('eyebrow_title', 'vi')).toBe('Trực quan hóa lộ trình tối ưu')
    expect(t('group_two_point', 'vi')).toBe('🔍 Tìm đường 2 điểm (Thuật toán đơn lẻ)')
    expect(t('group_multi_stop', 'vi')).toBe('📦 Giao hàng đa điểm (TSP)')
    expect(t('group_comparison', 'vi')).toBe('📊 So sánh thuật toán')
    expect(t('tour_itinerary_title', 'vi')).toBe('Lộ trình giao hàng từng chặng')
    expect(t('depot_badge', 'vi')).toBe('Trạm Depot')
  })

  it('interpolates parameters correctly', () => {
    expect(t('stops_needed', 'en', { count: 3 })).toBe('Need to select 3 more stop(s) (minimum 5 delivery stops).')
    expect(t('stops_needed', 'vi', { count: 3 })).toBe('Cần chọn thêm 3 điểm nữa (tối thiểu 5 điểm giao hàng).')
    expect(t('pick_hint_tour_goal', 'en', { count: 2, max: 10 })).toContain('(2/10)')
    expect(t('pick_hint_tour_goal', 'vi', { count: 2, max: 10 })).toContain('(2/10)')
    expect(t('tour_savings_badge', 'en', { dist: '3.20', time: '5.10', percent: '21.5' })).toBe('Saved 3.20 km · 5.10 min (21.5% cost reduction)')
    expect(t('tour_savings_badge', 'vi', { dist: '3.20', time: '5.10', percent: '21.5' })).toBe('Tiết kiệm: 3.20 km · 5.10 phút (Giảm 21.5% chi phí)')
    expect(t('stop_badge', 'en', { no: 1 })).toBe('Stop #1')
    expect(t('stop_badge', 'vi', { no: 1 })).toBe('Trạm #1')
  })

  it('translates graph label correctly based on selected language', () => {
    expect(translateGraphLabel('Thu Duc major landmarks road graph', 'en')).toBe('Thu Duc major landmarks road graph')
    expect(translateGraphLabel('Thu Duc major landmarks road graph', 'vi')).toBe('Mạng lưới giao thông các địa điểm chính TP. Thủ Đức')
  })
})
