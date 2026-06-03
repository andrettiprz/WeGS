import { t } from '../lib/i18n'

export default function Hero({ stationName = 'WeGS' }) {
    return (
        <section className="hero" id="inicio">
            <div className="hero__bg-gradient" />
            <div className="hero__orbit hero__orbit--inner" />
            <div className="hero__orbit" />
            <div className="hero__orbit hero__orbit--outer" />

            <div className="hero__content">
                <img src="./logo.png" alt="WeGS" className="hero__logo" />

                <div className="hero__label">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M12 1v6m0 6v6m-7.07-3.93 4.24-4.24m5.66-5.66 4.24-4.24M1 12h6m6 0h6m-3.93 7.07-4.24-4.24m-5.66-5.66L3.93 4.93" /></svg>
                    LIVE · {stationName}
                </div>

                <h1 className="hero__title">
                    {t('hero_title').split('<br />').length > 1 ? (
                        <>
                            {t('hero_title').split('<br />')[0]}<br />
                            <span>{t('hero_title').split('<br />')[1]}</span>
                        </>
                    ) : (
                        t('hero_title')
                    )}
                </h1>

                <p className="hero__description">
                    {t('hero_subtitle')}
                </p>

                <a href="#galeria" className="hero__cta">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="8.5" cy="8.5" r="1.5" /><path d="m21 15-5-5L5 21" /></svg>
                    {t('hero_cta')}
                </a>

                <div className="hero__stats-row">
                    <div className="hero__stat hero__stat--primary">
                        <div className="hero__stat-value">24/7</div>
                        <div className="hero__stat-label">{t('hero_monitoring')}</div>
                    </div>
                    <div className="hero__stat">
                        <div className="hero__stat-value">137 MHz</div>
                        <div className="hero__stat-label">{t('hero_frequency')}</div>
                    </div>
                    <div className="hero__stat">
                        <div className="hero__stat-value">LRPT</div>
                        <div className="hero__stat-label">{t('hero_protocol')}</div>
                    </div>
                    <div className="hero__stat">
                        <div className="hero__stat-value">MSU-MR</div>
                        <div className="hero__stat-label">{t('hero_instrument')}</div>
                    </div>
                </div>
            </div>
        </section>
    )
}
