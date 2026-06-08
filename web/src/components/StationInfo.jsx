import { t } from '../lib/i18n'

export default function StationInfo({
    stationName = 'WeGS',
    location = 'Ground Station',
    coordinates = '0.0000 N, 0.0000 W',
    mapSrc = '',
    outputFolder = '',
    passesCount = 0,
}) {
    return (
        <section className="section station" id="estacion">
            <div className="section__header">
                <div className="section__tag"><svg className="section__tag-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg> {t('station_tag')}</div>
                <h2 className="section__title">{stationName}</h2>
                <p className="section__subtitle">
                    {t('station_title')}
                </p>
            </div>

            <div className="station__grid">
                <div className="station__card">
                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_location_label')}</div>
                            <div className="station__detail-value">{location}</div>
                        </div>
                    </div>

                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_coords_label')}</div>
                            <div className="station__detail-value">{coordinates}</div>
                        </div>
                    </div>

                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" /><path d="M8 21h8M12 17v4" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_data_source')}</div>
                            <div className="station__detail-value station__detail-value--mono">
                                {outputFolder || t('station_data_local')}
                            </div>
                        </div>
                    </div>

                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_passes_label')}</div>
                            <div className="station__detail-value">{passesCount} {t('station_passes_total')}</div>
                        </div>
                    </div>
                </div>

                {mapSrc && (
                    <div className="station__map">
                        <iframe
                            title={stationName}
                            src={mapSrc}
                            allowFullScreen=""
                            loading="lazy"
                            referrerPolicy="no-referrer-when-downgrade"
                        />
                    </div>
                )}
            </div>
        </section>
    )
}
