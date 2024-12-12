import React, { useEffect, useRef, useState } from 'react';
import L, { Tooltip } from 'leaflet';
import polyline from 'polyline-encoded';
import 'leaflet/dist/leaflet.css';
import styled from 'styled-components';
import { throttle } from 'lodash';

const api_base_address = process.env.REACT_APP_API_BASE_URL

const StyledMap = styled.div`
    height: 100%;
    width: 100%;
    `;

// Correct Leaflet icons path
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});


export default function MapDisplay({ years, selectedAthletes }) {
    const [routesData, setRoutesData] = useState([]);
    const mapRef = useRef(null);
    const highlightedRoutesGroupRef = useRef(null);
    const isZoomingRef = useRef(false); // Ref to track zooming state


    useEffect(() => {
        const clearHighlight = () => {
            // Function to clear any highlighted polyline copies
            if (highlightedRoutesGroupRef.current) {
                highlightedRoutesGroupRef.current.clearLayers(); // Remove all layers from the highlighted group
            }
        };
        // Only initialize the map if it doesn't already exist
        if (!mapRef.current) {
            const map = L.map('map', {
                center: [0, 0],
                zoom: 3,
                maxZoom: 22,
                minZoom: 3,
                maxBounds: [[-90, -180], [90, 180]], // Limit the view to a single world
                maxBoundsViscosity: 1.0, // Makes it harder to drag the map outside of maxBounds
            });
            map.on('mouseout', clearHighlight); // Mouse leaves the map area
            map.on('movestart', clearHighlight); // Starts moving the map
            map.on('zoomstart', clearHighlight); // Starts zooming the map

            mapRef.current = map;

            // Initialize layer groups and add them to the map
            highlightedRoutesGroupRef.current = L.layerGroup().addTo(map);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
                noWrap: true,
            }).addTo(map);

            // Set isZoomingRef to true when zoom starts
            map.on('zoomstart', () => {
                isZoomingRef.current = true;
            });

            // Set isZoomingRef to false when zoom ends
            map.on('zoomend', () => {
                isZoomingRef.current = false;
            });

        }
        const fetchData = async () => {
            try {
                const url = new URL(api_base_address + '/map/');
                const athleteIds = selectedAthletes.map(athlete => athlete.athlete_id);
                const params = {
                    years: years.join(','), // Join years into a comma-separated string
                    athletes: athleteIds.join(','), // Join athlete IDs into a comma-separated string
                };
                url.search = new URLSearchParams(params).toString();

                const response = await fetch(url);
                const data = await response.json();

                setRoutesData(data);
                displayRoutes(data, mapRef.current, selectedAthletes, highlightedRoutesGroupRef.current, isZoomingRef);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
        // Cleanup function to run when the component unmounts
        return () => {
            if (mapRef.current) {
                // Cleanup event listeners
                mapRef.current.off('mouseout', clearHighlight);
                mapRef.current.off('movestart', clearHighlight);
                mapRef.current.off('zoomstart', clearHighlight);
                mapRef.current.remove(); // Properly remove the map instance
                mapRef.current = null;

            }
        };
    }, [years, selectedAthletes]);

    return (
        <StyledMap id="map" />
    );
};

const displayRoutes = (data, map, selectedAthletes, highlightedRoutesGroup, isZoomingRef) => {
    // Clear existing highlighted layers
    highlightedRoutesGroup.clearLayers();

    let allBounds = [];
    data.forEach(activity => {
        const athleteColor =
            selectedAthletes.find(a => a.athlete_id.toString() === activity.athlete_id.toString())?.color || 'red';

        if (activity.summary_polyline && activity.summary_polyline.coordinates.length > 1) {
            // Use polyline's coordinates directly
            const latLngs = activity.summary_polyline.coordinates.map(([lng, lat]) => [lat, lng]); // Flip coordinates

            // Original route polyline
            const routePolyline = L.polyline(latLngs, {
                color: athleteColor,
                opacity: 1,
                weight: 2,
            }).addTo(map); // Add to the map directly

            routePolyline.on(
                'mouseover',
                throttle(function () {
                    if (!isZoomingRef.current) {
                        // Highlighted copy
                        const highlightedCopy = L.polyline(this.getLatLngs(), {
                            color: '#fff',
                            opacity: 1,
                            weight: 5,
                        }).addTo(highlightedRoutesGroup);
                        const polylineElement = highlightedCopy._path;
                        if (polylineElement) {
                            polylineElement.style.pointerEvents = 'none';
                        }
                        this._highlightedCopy = highlightedCopy;
                    }
                }, 100)
            );

            routePolyline.on(
                'mouseout',
                throttle(function () {
                    if (this._highlightedCopy) {
                        highlightedRoutesGroup.removeLayer(this._highlightedCopy);
                        delete this._highlightedCopy;
                    }
                }, 100)
            );

            routePolyline.on('click', function (e) {
                const popupContent = `
                    <strong>Activity Name:</strong> ${activity.name}<br>
                    <strong>Athlete ID:</strong> ${activity.athlete_id}<br>
                    <strong>Activity ID:</strong> ${activity.activity_id}<br>
                    <a href="${activity.url}" target="_blank">View Activity</a>
                `;

                const popup = L.popup()
                    .setLatLng(e.latlng)
                    .setContent(popupContent)
                    .openOn(map);
            });

            allBounds.push(routePolyline.getBounds());
        }
    });

    // Fit map bounds
    if (allBounds.length > 0) {
        const combinedBounds = allBounds.reduce((acc, bounds) => acc.extend(bounds), L.latLngBounds(allBounds[0]));
        map.fitBounds(combinedBounds);
    }
};

