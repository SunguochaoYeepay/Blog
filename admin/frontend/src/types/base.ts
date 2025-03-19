import type { TableProps, TablePaginationConfig } from 'ant-design-vue/es/table'
import type { FilterValue, SorterResult } from 'ant-design-vue/es/table/interface'

export type TableChangeHandler = (
  pagination: TablePaginationConfig,
  filters: Record<string, FilterValue | null>,
  sorter: SorterResult<any> | SorterResult<any>[]
) => void

export interface BaseListProps {
  columns: any[]
  dataSource: any[]
  loading?: boolean
  pagination?: TablePaginationConfig
  searchForm?: any
  rowKey?: string | ((record: any) => string)
}

export interface BaseListEmits {
  (e: 'search'): void
  (e: 'reset'): void
  (e: 'table-change', pagination: TablePaginationConfig, filters: Record<string, FilterValue | null>, sorter: SorterResult<any> | SorterResult<any>[]): void
}