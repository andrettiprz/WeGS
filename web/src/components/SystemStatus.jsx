import { t, getLang } from '../lib/i18n'

export default function SystemStatus({ error }) {
    const locale = getLang() === 'es' ? 'es-MX' : 'en-US'
    const lastHeartbeat = new Date().toLocaleString(locale, {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: false,
    })

    return (
        <section className="section">
            <div className="section__header">
                <div className="section__tag">{t('system_tag')}</div>
                <h2 className="section__title">{t('system_status')}</h2>
            </div>

            <div className="system-status__container">
                <div className="system-status__main">
                    <div className={`system-status__indicator ${error ? 'system-status__indicator--error' : 'system-status__indicator--online'}`}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
                    </div>
                    <div>
                        <div className="system-status__label">{t('nav_station')}</div>
                        <div className={`system-status__value ${error ? 'system-status__value--error' : 'system-status__value--online'}`}>
                            {error ? t('system_offline') : t('system_online')}
                        </div>
                        {error && (
                            <div className="system-status__error">
                                {error}
                            </div>
                        )}
                    </div>
                </div>

                <div className="system-status__details">
                    <div className="system-status__detail">
                        <div className="system-status__detail-value">{error ? '—' : '1.0'}</div>
                        <div className="system-status__detail-label">{t('status_bot_version')}</div>
                    </div>
                    <div className="system-status__detail">
                        <div className="system-status__detail-value">{lastHeartbeat}</div>
                        <div className="system-status__detail-label">{t('system_last_update')}</div>
                    </div>
                    <div className="system-status__detail">
                        <div className="system-status__detail-value">{error ? '—' : t('system_source_local')}</div>
                        <div className="system-status__detail-label">{t('system_data_source')}</div>
                    </div>
                </div>
            </div>
        </section>
    )
}
