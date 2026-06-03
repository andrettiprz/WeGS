import { useEffect, useState } from 'react'
import { formatTimeLong } from '../lib/formatDate'
import { t } from '../lib/i18n'

export default function Lightbox({ images, currentIndex = 0, pass, onClose }) {
    const [index, setIndex] = useState(currentIndex)
    const [zoom, setZoom] = useState(1)
    const [position, setPosition] = useState({ x: 0, y: 0 })
    const [isDragging, setIsDragging] = useState(false)
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

    useEffect(() => {
        setIndex(currentIndex)
    }, [currentIndex])

    useEffect(() => {
        setZoom(1)
        setPosition({ x: 0, y: 0 })
    }, [index])

    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === 'Escape') onClose()
            if (e.key === 'ArrowRight' && index < images.length - 1) setIndex(i => i + 1)
            if (e.key === 'ArrowLeft' && index > 0) setIndex(i => i - 1)
        }
        document.addEventListener('keydown', handleKey)
        document.body.style.overflow = 'hidden'
        return () => {
            document.removeEventListener('keydown', handleKey)
            document.body.style.overflow = ''
        }
    }, [onClose, index, images.length])

    const handleWheel = (e) => {
        e.preventDefault()
        const delta = e.deltaY > 0 ? -0.25 : 0.25
        setZoom(prev => Math.min(5, Math.max(0.5, prev + delta)))
    }

    const toggleZoom = () => {
        if (zoom > 1) {
            setZoom(1)
            setPosition({ x: 0, y: 0 })
        } else {
            setZoom(2)
        }
    }

    const handleMouseDown = (e) => {
        if (zoom > 1) {
            setIsDragging(true)
            setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y })
        }
    }

    const handleMouseMove = (e) => {
        if (isDragging && zoom > 1) {
            setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
        }
    }

    const handleMouseUp = () => setIsDragging(false)

    const handleTouchStart = (e) => {
        if (zoom > 1 && e.touches.length === 1) {
            setIsDragging(true)
            setDragStart({ x: e.touches[0].clientX - position.x, y: e.touches[0].clientY - position.y })
        }
    }

    const handleTouchMove = (e) => {
        if (isDragging && zoom > 1) {
            setPosition({ x: e.touches[0].clientX - dragStart.x, y: e.touches[0].clientY - dragStart.y })
        }
    }
    const handleTouchEnd = () => setIsDragging(false)

    if (!images || images.length === 0) return null

    const current = images[index]

    return (
        <div className="lightbox" onClick={onClose}>
            <div className="lightbox__content" onClick={e => e.stopPropagation()}>
                <button className="lightbox__close" onClick={onClose} aria-label={t('lightbox_close')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 6 6 18M6 6l12 12" />
                    </svg>
                </button>

                {/* Left arrow */}
                {index > 0 && (
                    <button className="lightbox__nav lightbox__nav--prev" onClick={() => setIndex(i => i - 1)} aria-label={t('lightbox_prev')}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="m15 18-6-6 6-6" />
                        </svg>
                    </button>
                )}

                <div
                    className="lightbox__image-container"
                    style={{
                        transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
                        cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in',
                        transition: isDragging ? 'none' : 'transform 0.2s ease',
                    }}
                    onClick={(e) => { e.stopPropagation(); toggleZoom() }}
                    onDoubleClick={(e) => { e.stopPropagation(); toggleZoom() }}
                    onWheel={handleWheel}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                    onTouchStart={handleTouchStart}
                    onTouchMove={handleTouchMove}
                    onTouchEnd={handleTouchEnd}
                >
                    <img
                        src={current.image_url}
                        alt={current.label || current.type}
                    />
                </div>

                <div className="lightbox__zoom-controls">
                    <button
                        className="lightbox__zoom-btn"
                        onClick={(e) => { e.stopPropagation(); setZoom(prev => Math.min(5, prev + 0.5)) }}
                        aria-label={t('lightbox_zoom_in')}
                        title={t('lightbox_zoom_in')}
                    >+</button>
                    <button
                        className="lightbox__zoom-btn"
                        onClick={(e) => { e.stopPropagation(); setZoom(1); setPosition({x:0,y:0}) }}
                        aria-label={t('lightbox_zoom_reset')}
                        title={t('lightbox_zoom_reset')}
                    >{Math.round(zoom * 100)}%</button>
                    <button
                        className="lightbox__zoom-btn"
                        onClick={(e) => { e.stopPropagation(); setZoom(prev => Math.max(0.5, prev - 0.5)) }}
                        aria-label={t('lightbox_zoom_out')}
                        title={t('lightbox_zoom_out')}
                    >−</button>
                </div>

                {/* Right arrow */}
                {index < images.length - 1 && (
                    <button className="lightbox__nav lightbox__nav--next" onClick={() => setIndex(i => i + 1)} aria-label={t('lightbox_next')}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="m9 18 6-6-6-6" />
                        </svg>
                    </button>
                )}

                <div className="lightbox__info">
                    <div className="lightbox__sat">{pass?.satellite || 'Satellite'}</div>
                    <div className="lightbox__detail">
                        {current.label} · {current.type} · {formatTimeLong(pass?.timestamp)}
                    </div>
                    {images.length > 1 && (
                        <div className="lightbox__counter">
                            {index + 1} / {images.length}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
