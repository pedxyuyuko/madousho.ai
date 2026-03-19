export interface Flow {
  uuid: string
  name: string
  description: string | null
  plugin: string
  tasks: string[] | null
  status: 'created' | 'processing' | 'finished'
  flow_template: string | null
  created_at: string
}

export interface FlowListResponse {
  items: Flow[]
  total: number
  offset: number
  limit: number
}
