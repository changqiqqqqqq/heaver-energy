export function maskPhone(phone: string): string {
  const normalized = phone.trim()
  if (normalized.length < 7) {
    return normalized
  }
  return `${normalized.slice(0, 3)}****${normalized.slice(-4)}`
}

