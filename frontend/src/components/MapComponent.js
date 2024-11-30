import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import CustomMarkerIcon from "../assets/marker.svg"
// import L from 'leaflet';


const customIcon = L.icon({
    iconUrl: CustomMarkerIcon.src,
    iconSize: [28, 26], // Adjust the size as needed
    // Other icon options...
});

const MapComponent = (props) => {
    const [isMounted, setIsMounted] = useState(false);

    
    useEffect(() => {
        // To fix the map rendering issue
        setIsMounted(true)
        const L = require('leaflet');
        // delete L.Icon.Default.prototype._getIconUrl;

    }, []);
    return (
        isMounted && (<MapContainer center={[27.6338529, 85.5178667]} zoom={13} style={{ height: "100vh", width: "100%" }}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {props.activeMarker != null &&
                <Popup position={[props.buildings[props.activeMarker].latitude, props.buildings[props.activeMarker].longitude]}>
                    {props.buildings[props.activeMarker].hashes}
                </Popup>
            }
            {props.buildings.map((marker, index) => (
                <Marker key={index} position={[marker.latitude, marker.longitude]} icon={customIcon}>
                    <div className='h-full'>
                    <Popup>
                        
                        <p className='text-[8px]'>{marker.hashes}</p>
                        
                           
                        </Popup>
                        </div>
                </Marker>
            ))}
        </MapContainer>
    ));
};
export default MapComponent;
