import type { Component } from 'vue'

export interface MenuItem {
  label: string
  key: string
  icon?: Component
}