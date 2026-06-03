/**
 * Date formatting utilities.
 * Uses the current i18n language setting for locale-aware formatting.
 */

import { getLang } from './i18n'

function getLocale() {
  return getLang() === 'es' ? 'es-MX' : 'en-US'
}

/**
 * Local format without weekday.
 * Used by PassCard, PassesPage, PassDetailPage.
 */
export function formatTime(ts) {
  try {
    const d = new Date(ts)
    return d.toLocaleString(getLocale(), {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
    })
  } catch { return ts }
}

/**
 * Local format with weekday.
 * Used by Lightbox.
 */
export function formatTimeLong(ts) {
  try {
    const d = new Date(ts)
    return d.toLocaleString(getLocale(), {
      weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
    })
  } catch { return ts }
}

/**
 * UTC format.
 * Used by PassesPage, PassDetailPage.
 */
export function formatTimeUTC(ts) {
  try {
    const d = new Date(ts)
    return d.toLocaleString('en-US', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: false,
      timeZone: 'UTC',
    }) + ' UTC'
  } catch { return ts }
}
