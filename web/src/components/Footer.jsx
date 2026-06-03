import { t, getLang, setLang } from '../lib/i18n'

export default function Footer({
    stationName = 'WeGS',
    mapSrc = '',
    githubUrl = 'https://github.com',
}) {
    const currentLang = getLang()

    const toggleLang = () => {
        setLang(currentLang === 'en' ? 'es' : 'en')
        window.location.reload()
    }

    return (
        <footer className="footer">
            <div className="footer__brand">
                <img src="./logo.png" alt="WeGS" className="footer__logo" />
                <span className="footer__name">WeGS</span>
            </div>
            <p className="footer__text">
                {t('footer_text')}
            </p>

            {/* Language toggle */}
            <div className="footer__lang-toggle" style={{ marginBottom: '16px' }}>
                <button
                    onClick={toggleLang}
                    className="footer__link"
                    style={{ background: 'none', border: '1px solid var(--border)', padding: '6px 16px', borderRadius: '20px', cursor: 'pointer', fontSize: '0.8rem' }}
                    aria-label={t('toggle_lang')}
                >
                    {currentLang === 'en' ? t('lang_es') : t('lang_en')}
                </button>
            </div>

            <div className="footer__links">
                <a href={githubUrl} target="_blank" rel="noopener noreferrer" className="footer__link">
                    <svg className="inline-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 2 11 13M22 2 15 22 11 13 2 9z"/></svg> {t('footer_github')}
                </a>
            </div>

            {/* Google Maps embed at bottom if configured */}
            {mapSrc && (
                <div className="footer__map" style={{ marginTop: '24px', borderRadius: 'var(--radius)', overflow: 'hidden', border: '1px solid var(--border)', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto' }}>
                    <iframe
                        title={`${stationName} Map`}
                        src={mapSrc}
                        allowFullScreen=""
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                        style={{ width: '100%', height: '200px', border: 'none', filter: 'grayscale(0.7) brightness(0.6) contrast(1.2)' }}
                    />
                </div>
            )}
        </footer>
    )
}
