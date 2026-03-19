/**
 * Parchment Light Theme — Naive UI GlobalThemeOverrides
 *
 * Warm, medieval manuscript aesthetic with serif fonts and cream/parchment tones.
 * Designed to evoke the feel of an old tome or grimoire.
 */
import type { GlobalThemeOverrides } from 'naive-ui'

export const parchmentOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#8B4513',
    primaryColorHover: '#A0522D',
    primaryColorPressed: '#6B3410',
    primaryColorSuppl: '#A0522D',

    infoColor: '#5F726C',
    infoColorHover: '#6E827A',
    infoColorPressed: '#4D5E59',
    infoColorSuppl: '#5F726C',

    successColor: '#556B2F',
    successColorHover: '#657D3E',
    successColorPressed: '#465B21',
    successColorSuppl: '#556B2F',

    warningColor: '#B8860B',
    warningColorHover: '#CC9A1C',
    warningColorPressed: '#9A7209',
    warningColorSuppl: '#B8860B',

    errorColor: '#8B0000',
    errorColorHover: '#A00D0D',
    errorColorPressed: '#6E0000',
    errorColorSuppl: '#8B0000',

    bodyColor: '#F5E6C8',
    cardColor: '#EDE0CC',
    modalColor: '#EDE0CC',
    popoverColor: '#EDE0CC',
    tableColor: '#F0E4CC',
    inputColor: '#F0E4CC',
    actionColor: '#E8D5B8',
    tableHeaderColor: '#E2D4BC',
    tableColorHover: '#E8D5B8',
    tableColorStriped: '#EDE0CC',
    hoverColor: '#E8D5B8',
    pressedColor: '#DCC8A8',

    textColor1: '#3D2B1F',
    textColor2: 'rgba(61, 43, 31, 0.7)',
    textColor3: 'rgba(61, 43, 31, 0.5)',
    textColorDisabled: 'rgba(61, 43, 31, 0.35)',

    borderColor: 'rgba(93, 58, 26, 0.3)',
    dividerColor: 'rgba(93, 58, 26, 0.2)',

    scrollbarColor: 'rgba(139, 69, 19, 0.3)',
    scrollbarColorHover: 'rgba(139, 69, 19, 0.5)',

    fontFamily:
      "'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

    // Structural (match Starry Night — only colors differ)
    borderRadius: '8px',
    borderRadiusSmall: '4px',
    boxShadow1: '0 1px 2px -2px rgba(61, 43, 31, 0.08), 0 3px 6px 0 rgba(61, 43, 31, 0.06)',
    boxShadow2: '0 3px 6px -4px rgba(61, 43, 31, 0.1), 0 6px 16px 0 rgba(61, 43, 31, 0.08)',
    boxShadow3: '0 6px 16px -8px rgba(61, 43, 31, 0.12), 0 9px 28px 0 rgba(61, 43, 31, 0.1)'
  },

  Button: {
    // Default button text
    textColor: '#3D2B1F',
    textColorHover: '#3D2B1F',
    textColorPressed: '#3D2B1F',
    textColorFocus: '#3D2B1F',
    textColorDisabled: 'rgba(61, 43, 31, 0.35)',
    // Primary
    colorPrimary: '#8B4513',
    colorHoverPrimary: '#A0522D',
    colorPressedPrimary: '#6B3410',
    colorFocusPrimary: '#8B4513',
    colorDisabledPrimary: 'rgba(139, 69, 19, 0.35)',
    borderPrimary: '1px solid #8B4513',
    borderHoverPrimary: '1px solid #A0522D',
    borderPressedPrimary: '1px solid #6B3410',
    borderFocusPrimary: '1px solid #8B4513',
    borderDisabledPrimary: '1px solid rgba(139, 69, 19, 0.2)',
    textColorPrimary: '#F5E6C8',
    textColorHoverPrimary: '#F5E6C8',
    textColorPressedPrimary: '#F5E6C8',
    textColorFocusPrimary: '#F5E6C8',
    textColorDisabledPrimary: 'rgba(245, 230, 200, 0.5)',
    // Info
    colorInfo: '#5F726C',
    colorHoverInfo: '#6E827A',
    colorPressedInfo: '#4D5E59',
    textColorInfo: '#F5E6C8',
    textColorHoverInfo: '#F5E6C8',
    textColorPressedInfo: '#F5E6C8',
    borderInfo: '1px solid #5F726C',
    // Success
    colorSuccess: '#556B2F',
    colorHoverSuccess: '#657D3E',
    colorPressedSuccess: '#465B21',
    textColorSuccess: '#F5E6C8',
    textColorHoverSuccess: '#F5E6C8',
    textColorPressedSuccess: '#F5E6C8',
    borderSuccess: '1px solid #556B2F',
    // Warning
    colorWarning: '#B8860B',
    colorHoverWarning: '#CC9A1C',
    colorPressedWarning: '#9A7209',
    textColorWarning: '#F5E6C8',
    textColorHoverWarning: '#F5E6C8',
    textColorPressedWarning: '#F5E6C8',
    borderWarning: '1px solid #B8860B',
    // Error
    colorError: '#8B0000',
    colorHoverError: '#A00D0D',
    colorPressedError: '#6E0000',
    textColorError: '#F5E6C8',
    textColorHoverError: '#F5E6C8',
    textColorPressedError: '#F5E6C8',
    borderError: '1px solid #8B0000',
    // Quaternary
    colorQuaternary: '#E8D5B8',
    colorQuaternaryHover: '#DCC8A8',
    colorQuaternaryPressed: '#D0BA98',
    textColorQuaternary: '#3D2B1F',
    textColorQuaternaryHover: '#3D2B1F',
    textColorQuaternaryPressed: '#3D2B1F',
    // Border defaults
    border: '1px solid rgba(93, 58, 26, 0.3)',
    borderHover: '1px solid rgba(93, 58, 26, 0.5)',
    borderPressed: '1px solid rgba(93, 58, 26, 0.6)',
  },

  Input: {
    color: '#F0E4CC',
    colorFocus: '#EDE0CC',
    colorDisabled: '#E8D5B8',
    border: '1px solid rgba(93, 58, 26, 0.3)',
    borderHover: '1px solid rgba(139, 69, 19, 0.4)',
    borderFocus: '1px solid #8B4513',
    borderDisabled: '1px solid rgba(93, 58, 26, 0.2)',
    textColor: '#3D2B1F',
    textColorDisabled: 'rgba(61, 43, 31, 0.35)',
    caretColor: '#8B4513',
    placeholderColor: 'rgba(61, 43, 31, 0.4)',
    placeholderColorDisabled: 'rgba(61, 43, 31, 0.3)',
    iconColor: 'rgba(61, 43, 31, 0.5)',
    iconColorDisabled: 'rgba(61, 43, 31, 0.3)',
    iconColorHover: '#8B4513',
    suffixTextColor: 'rgba(61, 43, 31, 0.5)',
    countTextColor: 'rgba(61, 43, 31, 0.5)',
    boxShadowFocus: '0 0 0 2px rgba(139, 69, 19, 0.2)',
  },

  Card: {
    color: '#EDE0CC',
    colorModal: '#EDE0CC',
    colorPopover: '#EDE0CC',
    colorTarget: '#8B4513',
    borderColor: 'rgba(93, 58, 26, 0.2)',
    borderColorModal: 'rgba(93, 58, 26, 0.2)',
    borderColorPopover: 'rgba(93, 58, 26, 0.2)',
    borderRadius: '12px',
    boxShadow: '0 1px 2px -2px rgba(61, 43, 31, 0.08), 0 3px 6px 0 rgba(61, 43, 31, 0.06)',
    titleTextColor: '#3D2B1F',
    titleFontWeight: '600',
    textColor: 'rgba(61, 43, 31, 0.9)'
  },

  Select: {
    peers: {
      InternalSelection: {
        color: '#F0E4CC',
        colorActive: '#EDE0CC',
        border: '1px solid rgba(93, 58, 26, 0.3)',
        borderActive: '1px solid #8B4513',
        borderHover: '1px solid rgba(139, 69, 19, 0.4)',
        borderFocus: '1px solid #8B4513',
        textColor: '#3D2B1F',
        placeholderColor: 'rgba(61, 43, 31, 0.4)',
        caretColor: '#8B4513',
        boxShadowFocus: '0 0 0 2px rgba(139, 69, 19, 0.2)'
      }
    }
  },

  Menu: {
    itemColorHover: 'rgba(139, 69, 19, 0.1)',
    itemColorActive: 'rgba(139, 69, 19, 0.12)',
    itemColorActiveHover: 'rgba(139, 69, 19, 0.15)',
    itemTextColor: '#3D2B1F',
    itemTextColorHover: '#8B4513',
    itemTextColorActive: '#8B4513',
    itemTextColorActiveHover: '#8B4513',
    itemTextColorChildActive: '#8B4513',
    itemTextColorChildActiveHover: '#8B4513',
    itemIconColor: 'rgba(61, 43, 31, 0.7)',
    itemIconColorHover: '#8B4513',
    itemIconColorActive: '#8B4513',
    itemIconColorActiveHover: '#8B4513',
    itemIconColorChildActive: '#8B4513',
    itemIconColorChildActiveHover: '#8B4513',
    arrowColor: 'rgba(61, 43, 31, 0.5)',
    arrowColorHover: '#8B4513',
    arrowColorActive: '#8B4513',
    arrowColorActiveHover: '#8B4513',
    barColor: '#8B4513'
  },

  Tag: {
    colorPrimary: 'rgba(139, 69, 19, 0.12)',
    colorHoverPrimary: 'rgba(139, 69, 19, 0.18)',
    colorPressedPrimary: 'rgba(139, 69, 19, 0.22)',
    borderPrimary: '1px solid rgba(139, 69, 19, 0.3)',
    textColorPrimary: '#8B4513',
    borderRadius: '6px'
  },

  Tabs: {
    tabTextColorLine: 'rgba(61, 43, 31, 0.6)',
    tabTextColorActiveLine: '#8B4513',
    tabTextColorHoverLine: '#A0522D',
    barColor: '#8B4513'
  },

  DataTable: {
    borderColor: 'rgba(93, 58, 26, 0.15)',
    thColor: '#E2D4BC',
    thTextColor: '#3D2B1F',
    tdColor: '#F0E4CC',
    tdColorHover: '#E8D5B8',
    tdColorStriped: '#EDE0CC',
    tdTextColor: '#3D2B1F',
    thFontWeight: '600'
  },

  Modal: {
    color: '#EDE0CC',
    borderRadius: '12px',
    boxShadow: '0 6px 16px -8px rgba(61, 43, 31, 0.12), 0 9px 28px 0 rgba(61, 43, 31, 0.1)'
  },

  Tooltip: {
    color: '#3D2B1F',
    textColor: '#F5E6C8',
    borderRadius: '6px'
  },

  Message: {
    color: '#EDE0CC',
    colorWarning: 'rgba(184, 134, 11, 0.12)',
    colorError: 'rgba(139, 0, 0, 0.12)',
    colorSuccess: 'rgba(85, 107, 47, 0.12)',
    colorInfo: 'rgba(95, 114, 108, 0.12)',
    textColor: '#3D2B1F',
    borderRadius: '10px',
    boxShadow: '0 3px 6px -4px rgba(61, 43, 31, 0.1), 0 6px 16px 0 rgba(61, 43, 31, 0.08)'
  },

  Notification: {
    color: '#EDE0CC',
    borderRadius: '10px',
    borderColor: 'rgba(93, 58, 26, 0.2)',
    headerTextColor: '#3D2B1F',
    descriptionTextColor: 'rgba(61, 43, 31, 0.7)',
    actionTextColor: '#8B4513',
    closeIconColor: 'rgba(61, 43, 31, 0.5)',
    closeIconColorHover: '#3D2B1F',
    closeColorHover: 'rgba(139, 69, 19, 0.1)'
  },

  Breadcrumb: {
    itemTextColor: 'rgba(61, 43, 31, 0.7)',
    itemTextColorHover: '#8B4513',
    itemTextColorPressed: '#6B3410',
    itemTextColorActive: '#8B4513',
    separatorColor: 'rgba(61, 43, 31, 0.4)'
  },

  Switch: {
    railColor: 'rgba(93, 58, 26, 0.25)',
    railColorActive: '#8B4513',
    buttonColor: '#F5E6C8'
  },

  Checkbox: {
    colorChecked: '#8B4513',
    border: '1px solid rgba(93, 58, 26, 0.4)',
    borderChecked: '1px solid #8B4513',
    borderFocus: '1px solid #A0522D',
    boxShadowFocus: '0 0 0 2px rgba(139, 69, 19, 0.2)',
    textColor: '#3D2B1F'
  },

  Radio: {
    dotColorActive: '#8B4513',
    boxShadowActive: 'inset 0 0 0 1px #8B4513',
    boxShadowFocus: '0 0 0 2px rgba(139, 69, 19, 0.2)',
    border: '1px solid rgba(93, 58, 26, 0.4)',
    borderChecked: '1px solid #8B4513',
    borderFocus: '1px solid #A0522D'
  },

  Progress: {
    fillColor: '#8B4513',
    fillColorInfo: '#5F726C',
    fillColorSuccess: '#556B2F',
    fillColorWarning: '#B8860B',
    fillColorError: '#8B0000',
    railColor: 'rgba(93, 58, 26, 0.15)'
  },

  Dropdown: {
    color: '#EDE0CC',
    borderRadius: '8px',
    boxShadow: '0 2px 12px rgba(61, 43, 31, 0.15), 0 0 0 1px rgba(93, 58, 26, 0.15)',
    optionTextColor: '#3D2B1F',
    optionTextColorHover: '#3D2B1F',
    optionTextColorActive: '#8B4513',
    optionTextColorChildActive: '#8B4513',
    prefixColor: 'rgba(61, 43, 31, 0.5)',
    suffixColor: 'rgba(61, 43, 31, 0.5)',
    optionColorHover: 'rgba(139, 69, 19, 0.12)',
    optionColorActive: 'rgba(139, 69, 19, 0.15)',
    dividerColor: 'rgba(93, 58, 26, 0.2)',
  },
}
