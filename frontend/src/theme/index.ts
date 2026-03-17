import type { GlobalThemeOverrides } from 'naive-ui';
import { starryNightOverrides } from './starry-night';
import { parchmentOverrides } from './parchment';

export type ThemeName = 'starry-night' | 'parchment';

export function getThemeOverrides(name: ThemeName): GlobalThemeOverrides {
  switch (name) {
    case 'starry-night':
      return starryNightOverrides;
    case 'parchment':
      return parchmentOverrides;
    default:
      throw new Error(`Unknown theme name: ${name}`);
  }
}

export { starryNightOverrides } from './starry-night';
export { parchmentOverrides } from './parchment';