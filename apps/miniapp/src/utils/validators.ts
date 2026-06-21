export function isPresent(value: unknown): boolean {
  return value !== undefined && value !== null && value !== ''
}

export function isChinaMobile(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value.trim())
}

export function normalizeText(value: string): string {
  return value.trim()
}

