import Hero from '../components/Hero'
import Gallery from '../components/Gallery'
import SystemStatus from '../components/SystemStatus'
import Stats from '../components/Stats'
import StationInfo from '../components/StationInfo'

export default function HomePage({ passes, loading, error, stationName = 'WeGS' }) {
    const config = window.__WEGS_CONFIG__ || {}
    return (
        <>
            <Hero stationName={stationName} />
            <Gallery passes={passes.filter(p => p.images && p.images.length > 0)} loading={loading} />
            <SystemStatus error={error} />
            <Stats passes={passes} />
            <StationInfo
                stationName={config.stationName || stationName}
                location={config.location || 'Ground Station'}
                coordinates={config.coordinates || '0.0000° N, 0.0000° W'}
                mapSrc={config.mapSrc || ''}
                satellites={config.satellites || 'METEOR M2, M2-3, M2-4, M2-X'}
                frequency={config.frequency || '137.1 MHz / 137.9 MHz (VHF Band)'}
                software={config.software || 'SatDump — Live LRPT Decoding'}
            />
        </>
    )
}
