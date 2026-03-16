import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface ExampleState {
  items: string[]
  isLoading: boolean
}

export const useExampleStore = defineStore('example', () => {
  const items = ref<ExampleState['items']>([])
  const isLoading = ref<ExampleState['isLoading']>(false)

  const itemCount = computed(() => items.value.length)
  const hasItems = computed(() => items.value.length > 0)

  function setItems(newItems: string[]) {
    items.value = newItems
  }

  function clearItems() {
    items.value = []
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  return {
    items,
    isLoading,
    itemCount,
    hasItems,
    setItems,
    clearItems,
    setLoading,
  }
})
