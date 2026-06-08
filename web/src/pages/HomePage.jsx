import Hero from '../components/Hero'
import Gallery from '../components/Gallery'
import SystemStatus from '../components/SystemStatus'
import Stats from '../components/Stats'
import StationInfo from '../components/StationInfo'

export default function HomePage({ passes, loading, error, stationName = 'WeGS' }) {
    const config = window.__WEGS_CONFIG__ || {}
    const location = config.location || 'Ground Station'
    const coordinates = config.coordinates || '0.0000 N, 0.0000 W'
    const mapSrc = config.maps_embed_url || ''
    const outputFolder = config.output_folder || ''

    return (
        <>
            <Hero stationName={stationName} />
            <Gallery passes={passes.filter(p => p.images && p.images.length > 0)} loading={loading} />
            <SystemStatus error={error} />
            <Stats passes={passes} />
            <StationInfo
                stationName={stationName}
                location={location}
                coordinates={coordinates}
                mapSrc={mapSrc}
                outputFolder={outputFolder}
                passesCount={passes.length}
            />
        </>
    )
}
