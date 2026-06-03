import PassCard from './PassCard'
import { t } from '../lib/i18n'

export default function Gallery({ passes, loading }) {
    return (
        <section className="section" id="galeria">
            <div className="section__header">
                <div className="section__tag">
                    <svg className="section__tag-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9M7.8 16.2a7 7 0 0 1 0-8.4M16.2 7.8a7 7 0 0 1 0 8.4M19.1 4.9C23 8.8 23 15.2 19.1 19.1"/><circle cx="12" cy="12" r="1"/></svg> {t('gallery_tag')}
                </div>
                <h2 className="section__title">{t('gallery_title')}</h2>
                <p className="section__subtitle">
                    {t('gallery_subtitle')}
                </p>
            </div>

            {loading ? (
                <div className="loading-state">
                    <div className="loading-spinner" />
                    {t('gallery_loading')}
                </div>
            ) : (
                <div className="gallery__grid">
                    {passes.slice(0, 6).map(pass => (
                        <PassCard key={pass.id} pass={pass} />
                    ))}
                </div>
            )}
        </section>
    )
}
