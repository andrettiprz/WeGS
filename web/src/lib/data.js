/**
 * WeGS — Local data source.
 * Reads pass data from a manifest.json file (local or remote).
 * No Supabase required.
 */

const MANIFEST_URL = import.meta.env.VITE_MANIFEST_URL || '/manifest.json'

/**
 * Fetch all passes from the manifest.
 * Returns an empty array on failure.
 */
export async function fetchPasses() {
  try {
    const resp = await fetch(MANIFEST_URL)
    if (!resp.ok) return []
    const data = await resp.json()
    return (data.passes || []).map(p => ({
      id: p.folder_name,
      satellite: p.satellite,
      timestamp: p.timestamp,
      folder_name: p.folder_name,
      pngCount: p.png_count || 0,
      rawCount: p.raw_count || 0,
      filledCount: p.filled_count || 0,
      status: p.status || 'completed',
      images: (p.images || []).map(img => ({
        id: img.image_path || img.label,
        type: img.type,
        label: img.label,
        image_url: img.image_path,
        thumbnail_url: img.thumbnail_path || img.image_path,
      })),
    }))
  } catch {
    return []
  }
}

/**
 * Fetch a single pass by ID from the manifest.
 */
export async function fetchPassById(passId) {
  try {
    const passes = await fetchPasses()
    return passes.find(p => p.id === passId) || null
  } catch {
    return null
  }
}
