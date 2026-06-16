export function formatEmpty(value: unknown): string {
  return value === undefined || value === null || value === '' ? '-' : String(value)
}

