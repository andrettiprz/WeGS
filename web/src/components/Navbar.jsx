import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { t } from '../lib/i18n'

export default function Navbar({ passes = [], stationName = 'WeGS' }) {
    const location = useLocation()
    const isHome = location.pathname === '/'
    const [menuOpen, setMenuOpen] = useState(false)
    const [scrolled, setScrolled] = useState(false)

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 10)
        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    const closeMenu = () => setMenuOpen(false)

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <Link to="/" className="navbar__brand">
                <img src="./logo.png" alt="WeGS Logo" className="navbar__logo" />
                <div>
                    <div className="navbar__name">WeGS</div>
                    <div className="navbar__sub">{stationName}</div>
                </div>
            </Link>
            <div className="navbar__links">
                {isHome ? (
                    <a href="#galeria">{t('nav_gallery')}</a>
                ) : (
                    <Link to="/#galeria">{t('nav_gallery')}</Link>
                )}
                <Link to="/pases" className={location.pathname === '/pases' ? 'navbar__link--active' : ''}>
                    {t('nav_passes')}
                </Link>
                {isHome ? (
                    <a href="#estacion">{t('nav_station')}</a>
                ) : (
                    <Link to="/#estacion">{t('nav_station')}</Link>
                )}
                {isHome ? (
                    <a href="#estadisticas">{t('nav_stats')}</a>
                ) : (
                    <Link to="/#estadisticas">{t('nav_stats')}</Link>
                )}
            </div>
            <button
                className={`navbar__hamburger ${menuOpen ? 'navbar__hamburger--open' : ''}`}
                onClick={() => setMenuOpen(prev => !prev)}
                aria-label={menuOpen ? 'Close menu' : 'Open menu'}
                aria-expanded={menuOpen}
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <line x1="3" y1="6" x2="21" y2="6" className="hamburger__line hamburger__line--top" />
                    <line x1="3" y1="12" x2="21" y2="12" className="hamburger__line hamburger__line--mid" />
                    <line x1="3" y1="18" x2="21" y2="18" className="hamburger__line hamburger__line--bot" />
                </svg>
            </button>
            <div className="navbar__status">
                <span className="navbar__status-dot"></span>
                <span className="navbar__status-text">
                    {t('nav_live')}{passes.length > 0 ? ` — ${passes.length} ${t('nav_passes_count')}` : ''}
                </span>
            </div>
            <div className={`navbar__mobile-menu ${menuOpen ? 'navbar__mobile-menu--open' : ''}`}>
                {isHome ? (
                    <a href="#galeria" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_gallery')}</a>
                ) : (
                    <Link to="/#galeria" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_gallery')}</Link>
                )}
                <Link to="/pases" className={`navbar__mobile-link ${location.pathname === '/pases' ? 'navbar__link--active' : ''}`} onClick={closeMenu}>
                    {t('nav_passes')}
                </Link>
                {isHome ? (
                    <a href="#estacion" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_station')}</a>
                ) : (
                    <Link to="/#estacion" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_station')}</Link>
                )}
                {isHome ? (
                    <a href="#estadisticas" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_stats')}</a>
                ) : (
                    <Link to="/#estadisticas" className="navbar__mobile-link" onClick={closeMenu}>{t('nav_stats')}</Link>
                )}
                <div className="navbar__mobile-status">
                    <span className="navbar__status-dot"></span>
                    <span className="navbar__mobile-status-text">
                        {t('nav_live')}{passes.length > 0 ? ` — ${passes.length} ${t('nav_passes_count')}` : ''}
                    </span>
                </div>
            </div>
        </nav>
    )
}
