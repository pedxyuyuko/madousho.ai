import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const messages = {
  'zh-CN': {},
  'en-US': {},
}

const NDropdownStub = {
  props: ['options', 'trigger'],
  emits: ['select'],
  data() {
    return { visible: false }
  },
  template: `
    <div class="n-dropdown-stub">
      <div class="n-dropdown-trigger" @click="visible = !visible">
        <slot />
      </div>
      <ul v-if="visible" class="n-dropdown-options">
        <li
          v-for="opt in options"
          :key="opt.key"
          class="n-dropdown-option"
          @click="$emit('select', opt.key); visible = false"
        >
          {{ opt.label }}
        </li>
      </ul>
    </div>
  `,
}

function mountLanguageSwitcher(initialLocale: 'zh-CN' | 'en-US' = 'zh-CN') {
  const i18n = createI18n({
    legacy: false,
    locale: initialLocale,
    fallbackLocale: 'zh-CN',
    messages,
    missingWarn: false,
    fallbackWarn: false,
  })

  const wrapper = mount(LanguageSwitcher, {
    global: {
      plugins: [i18n],
      stubs: {
        'n-dropdown': NDropdownStub,
        NDropdown: NDropdownStub,
      },
    },
  })

  return {
    wrapper,
    i18n,
  }
}

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('renders the current locale and test id on the trigger', () => {
    const { wrapper } = mountLanguageSwitcher('zh-CN')

    const trigger = wrapper.get('[data-testid="language-switcher"]')
    expect(trigger.attributes('data-testid')).toBe('language-switcher')
    expect(wrapper.find('.language-switcher__label').text()).toBe('中文')
    expect(wrapper.find('.language-switcher__chevron').text()).toBe('▾')
  })

  it('shows exactly two locale options in the dropdown', async () => {
    const { wrapper } = mountLanguageSwitcher('zh-CN')

    await wrapper.find('.n-dropdown-trigger').trigger('click')

    const options = wrapper.findAll('.n-dropdown-option')
    expect(options).toHaveLength(2)
    expect(options[0]!.text()).toBe('✓ 中文')
    expect(options[1]!.text()).toBe('English')
  })

  it('updates vue-i18n locale when selecting a different locale', async () => {
    const { wrapper, i18n } = mountLanguageSwitcher('zh-CN')

    await wrapper.find('.n-dropdown-trigger').trigger('click')

    const options = wrapper.findAll('.n-dropdown-option')
    await options[1]!.trigger('click')

    expect(i18n.global.locale.value).toBe('en-US')
    expect(wrapper.find('.language-switcher__label').text()).toBe('English')
  })

  it('marks the current locale with a visible check indicator', async () => {
    const { wrapper } = mountLanguageSwitcher('en-US')

    await wrapper.find('.n-dropdown-trigger').trigger('click')

    const options = wrapper.findAll('.n-dropdown-option')
    expect(options[0]!.text()).toBe('中文')
    expect(options[1]!.text()).toBe('✓ English')
  })
})
