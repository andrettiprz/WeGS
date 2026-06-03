import { t } from '../lib/i18n'

export default function StationInfo({
    stationName = 'WeGS',
    location = 'Ground Station',
    coordinates = '0.0000° N, 0.0000° W',
    mapSrc = '',
    satellites = 'METEOR M2, M2-3, M2-4, M2-X',
    frequency = '137.1 MHz / 137.9 MHz (VHF Band)',
    software = 'SatDump — Live LRPT Decoding',
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
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9M7.8 16.2a7 7 0 0 1 0-8.4M16.2 7.8a7 7 0 0 1 0 8.4M19.1 4.9C23 8.8 23 15.2 19.1 19.1" /><circle cx="12" cy="12" r="1" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_freq_label')}</div>
                            <div className="station__detail-value">{frequency}</div>
                        </div>
                    </div>

                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.49 8.49 2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.49-8.49 2.83-2.83" /><circle cx="12" cy="12" r="4" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_satellites_label')}</div>
                            <div className="station__detail-value">{satellites}</div>
                        </div>
                    </div>

                    <div className="station__detail">
                        <div className="station__icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" /><path d="M8 21h8M12 17v4" /></svg>
                        </div>
                        <div>
                            <div className="station__detail-label">{t('station_software_label')}</div>
                            <div className="station__detail-value">{software}</div>
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
