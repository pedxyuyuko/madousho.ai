/**
 * Starry Night — A deep purple dark theme for Madousho.ai
 *
 * Inspired by the LoginView.vue glass-morphism aesthetic:
 * gradient from #0d0d1a → #1a1035 → #2d1b4e with glowing purple accents.
 */
import type { GlobalThemeOverrides } from 'naive-ui'

export const starryNightOverrides: GlobalThemeOverrides = {
  common: {
    // ── Brand (purple) ──────────────────────────────────────────────
    primaryColor: '#7c3aed',
    primaryColorHover: '#8b5cf6',
    primaryColorPressed: '#6d28d9',
    primaryColorSuppl: '#7c3aed',

    // ── Info (magic blue) ───────────────────────────────────────────
    infoColor: '#6366f1',
    infoColorHover: '#818cf8',
    infoColorPressed: '#4f46e5',
    infoColorSuppl: '#6366f1',

    // ── Success ─────────────────────────────────────────────────────
    successColor: '#22c55e',
    successColorHover: '#4ade80',
    successColorPressed: '#16a34a',
    successColorSuppl: '#22c55e',

    // ── Warning (star gold) ─────────────────────────────────────────
    warningColor: '#fbbf24',
    warningColorHover: '#fcd34d',
    warningColorPressed: '#f59e0b',
    warningColorSuppl: '#fbbf24',

    // ── Error ───────────────────────────────────────────────────────
    errorColor: '#ef4444',
    errorColorHover: '#f87171',
    errorColorPressed: '#dc2626',
    errorColorSuppl: '#ef4444',

    // ── Backgrounds ─────────────────────────────────────────────────
    bodyColor: '#0a0a14',
    cardColor: 'rgba(18, 16, 31, 0.85)',
    inputColor: 'rgba(18, 16, 31, 0.6)',
    modalColor: 'rgba(18, 16, 31, 0.92)',
    popoverColor: 'rgba(18, 16, 31, 0.9)',
    tableColor: 'rgba(18, 16, 31, 0.75)',
    tableColorHover: 'rgba(26, 16, 53, 0.5)',
    tableColorStriped: 'rgba(12, 10, 20, 0.5)',

    // ── Text ────────────────────────────────────────────────────────
    textColor1: '#e2dff0',
    textColor2: 'rgba(226, 223, 240, 0.65)',
    textColor3: 'rgba(226, 223, 240, 0.4)',

    // ── Borders & Dividers ──────────────────────────────────────────
    borderColor: 'rgba(124, 58, 237, 0.2)',
    dividerColor: 'rgba(124, 58, 237, 0.15)',

    // ── Actions (hover / press overlays) ────────────────────────────
    hoverColor: 'rgba(124, 58, 237, 0.12)',
    pressedColor: 'rgba(124, 58, 237, 0.2)',
    actionColor: 'rgba(18, 16, 31, 0.5)',

    // ── Scrollbar ───────────────────────────────────────────────────
    scrollbarColor: 'rgba(124, 58, 237, 0.3)',
    scrollbarColorHover: 'rgba(124, 58, 237, 0.5)',

    // ── Typography ──────────────────────────────────────────────────
    fontFamily:
      "'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

    // ── Misc ────────────────────────────────────────────────────────
    borderRadius: '8px',
    borderRadiusSmall: '4px',
    boxShadow1: '0 2px 12px 0 rgba(0, 0, 0, 0.4)',
    boxShadow2: '0 4px 24px 0 rgba(0, 0, 0, 0.5)',
    boxShadow3: '0 8px 48px 0 rgba(0, 0, 0, 0.6)',
  },

  // ── Component: Button ───────────────────────────────────────────
  Button: {
    // Default button text (critical for dark mode readability)
    textColor: '#e2dff0',
    textColorHover: '#e2dff0',
    textColorPressed: '#e2dff0',
    textColorFocus: '#e2dff0',
    textColorDisabled: 'rgba(226, 223, 240, 0.3)',
    // Primary
    colorPrimary: '#7c3aed',
    colorHoverPrimary: '#8b5cf6',
    colorPressedPrimary: '#6d28d9',
    colorFocusPrimary: '#7c3aed',
    colorDisabledPrimary: 'rgba(124, 58, 237, 0.35)',
    textColorPrimary: '#e2dff0',
    textColorHoverPrimary: '#e2dff0',
    textColorPressedPrimary: '#e2dff0',
    textColorDisabledPrimary: 'rgba(226, 223, 240, 0.5)',
    borderPrimary: '1px solid rgba(124, 58, 237, 0.5)',
    borderHoverPrimary: '1px solid #8b5cf6',
    borderPressedPrimary: '1px solid #6d28d9',
    borderDisabledPrimary: '1px solid rgba(124, 58, 237, 0.2)',
    rippleColorPrimary: '#8b5cf6',
    // Info
    colorInfo: '#6366f1',
    colorHoverInfo: '#818cf8',
    colorPressedInfo: '#4f46e5',
    textColorInfo: '#e2dff0',
    textColorHoverInfo: '#e2dff0',
    textColorPressedInfo: '#e2dff0',
    borderInfo: '1px solid rgba(99, 102, 241, 0.5)',
    // Success
    colorSuccess: '#22c55e',
    colorHoverSuccess: '#4ade80',
    colorPressedSuccess: '#16a34a',
    textColorSuccess: '#e2dff0',
    textColorHoverSuccess: '#e2dff0',
    textColorPressedSuccess: '#e2dff0',
    borderSuccess: '1px solid rgba(34, 197, 94, 0.5)',
    // Warning
    colorWarning: '#fbbf24',
    colorHoverWarning: '#fcd34d',
    colorPressedWarning: '#f59e0b',
    textColorWarning: '#1a1035',
    textColorHoverWarning: '#1a1035',
    textColorPressedWarning: '#1a1035',
    borderWarning: '1px solid rgba(251, 191, 36, 0.5)',
    // Error
    colorError: '#ef4444',
    colorHoverError: '#f87171',
    colorPressedError: '#dc2626',
    textColorError: '#e2dff0',
    textColorHoverError: '#e2dff0',
    textColorPressedError: '#e2dff0',
    borderError: '1px solid rgba(239, 68, 68, 0.5)',
    // Quaternary (ghost/transparent buttons - ThemeSwitcher uses this)
    colorQuaternary: 'transparent',
    colorQuaternaryHover: 'rgba(124, 58, 237, 0.15)',
    colorQuaternaryPressed: 'rgba(124, 58, 237, 0.25)',
    textColorQuaternary: '#e2dff0',
    textColorQuaternaryHover: '#e2dff0',
    textColorQuaternaryPressed: '#e2dff0',
    // Ghost / default buttons hover states
    colorHover: 'rgba(124, 58, 237, 0.15)',
    colorPressed: 'rgba(124, 58, 237, 0.25)',
    rippleColor: 'rgba(124, 58, 237, 0.2)',
  },

  // ── Component: Input ────────────────────────────────────────────
  Input: {
    color: 'rgba(18, 16, 31, 0.6)',
    colorFocus: 'rgba(18, 16, 31, 0.75)',
    colorDisabled: 'rgba(18, 16, 31, 0.3)',
    border: '1px solid rgba(124, 58, 237, 0.2)',
    borderHover: '1px solid rgba(124, 58, 237, 0.35)',
    borderFocus: '1px solid #7c3aed',
    borderDisabled: '1px solid rgba(124, 58, 237, 0.1)',
    caretColor: '#8b5cf6',
    textColor: '#e2dff0',
    textColorDisabled: 'rgba(226, 223, 240, 0.3)',
    placeholderColor: 'rgba(226, 223, 240, 0.35)',
    placeholderColorDisabled: 'rgba(226, 223, 240, 0.2)',
    iconColor: 'rgba(226, 223, 240, 0.5)',
    iconColorDisabled: 'rgba(226, 223, 240, 0.2)',
    clearColor: 'rgba(226, 223, 240, 0.4)',
    clearColorHover: 'rgba(226, 223, 240, 0.6)',
    suffixTextColor: 'rgba(226, 223, 240, 0.5)',
  },

  // ── Component: Card ─────────────────────────────────────────────
  Card: {
    color: 'rgba(30, 25, 50, 0.95)',
    colorModal: 'rgba(30, 25, 50, 0.98)',
    borderRadius: '12px',
    borderColor: 'rgba(124, 58, 237, 0.3)',
    boxShadow: '0 4px 24px 0 rgba(0, 0, 0, 0.4)',
    titleTextColor: '#e2dff0',
    textColor: 'rgba(226, 223, 240, 0.9)',
  },

  // ── Component: Menu (sidebar navigation) ────────────────────────
  Menu: {
    itemTextColor: 'rgba(226, 223, 240, 0.65)',
    itemTextColorHover: '#e2dff0',
    itemTextColorActive: '#8b5cf6',
    itemTextColorActiveHover: '#8b5cf6',
    itemIconColor: 'rgba(226, 223, 240, 0.5)',
    itemIconColorHover: 'rgba(226, 223, 240, 0.7)',
    itemIconColorActive: '#8b5cf6',
    itemIconColorActiveHover: '#8b5cf6',
    itemColorHover: 'rgba(124, 58, 237, 0.08)',
    itemColorActive: 'rgba(124, 58, 237, 0.12)',
    itemColorActiveHover: 'rgba(124, 58, 237, 0.18)',
    borderRadius: '8px',
  },

  // ── Component: Tag / Badge ──────────────────────────────────────
  Tag: {
    borderRadius: '6px',
    border: '1px solid rgba(124, 58, 237, 0.25)',
    colorBordered: 'rgba(18, 16, 31, 0.6)',
  },

  // ── Component: Modal / Dialog ───────────────────────────────────
  Modal: {
    color: 'rgba(18, 16, 31, 0.95)',
    borderRadius: '12px',
    boxShadow: '0 8px 48px 0 rgba(0, 0, 0, 0.7)',
  },

  // ── Component: Tooltip ──────────────────────────────────────────
  Tooltip: {
    color: 'rgba(18, 16, 31, 0.92)',
    borderRadius: '6px',
    boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.5)',
    textColor: '#e2dff0',
  },

  // ── Component: Notification ─────────────────────────────────────
  Notification: {
    color: 'rgba(18, 16, 31, 0.92)',
    borderRadius: '10px',
    borderColor: 'rgba(124, 58, 237, 0.2)',
    boxShadow: '0 4px 24px 0 rgba(0, 0, 0, 0.5)',
  },

  // ── Component: Dropdown ────────────────────────────────────────
  Dropdown: {
    color: 'rgba(18, 16, 31, 0.95)',
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(124, 58, 237, 0.2)',
    optionTextColor: 'rgba(226, 223, 240, 0.85)',
    optionTextColorHover: '#e2dff0',
    optionTextColorActive: '#8b5cf6',
    optionTextColorChildActive: '#8b5cf6',
    prefixColor: 'rgba(226, 223, 240, 0.5)',
    suffixColor: 'rgba(226, 223, 240, 0.5)',
    optionColorHover: 'rgba(124, 58, 237, 0.15)',
    optionColorActive: 'rgba(124, 58, 237, 0.2)',
    dividerColor: 'rgba(124, 58, 237, 0.15)',
  },
}
