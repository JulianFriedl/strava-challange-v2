import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import styled from 'styled-components';
import { apiRequest } from '../../api';

const StyledMap = styled.div`
    height: 100%;
    width: 100%;
    `;

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});


export default function MapDisplay({ years, selectedAthletes }) {
    const [, setRoutesData] = useState([]);
    const mapRef = useRef(null);
    const highlightedRoutesGroupRef = useRef(null);
    const isZoomingRef = useRef(false); // Ref to track zooming state


    useEffect(() => {
        const clearHighlight = () => {
            if (highlightedRoutesGroupRef.current) {
                highlightedRoutesGroupRef.current.clearLayers(); // Remove all layers from the highlighted group
            }
        };
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

            highlightedRoutesGroupRef.current = L.layerGroup().addTo(map);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
                noWrap: true,
            }).addTo(map);

            map.on('zoomstart', () => {
                isZoomingRef.current = true;
            });

            map.on('zoomend', () => {
                isZoomingRef.current = false;
            });

        }

        const fetchData = async () => {
            if (years.length === 0 || selectedAthletes.length === 0) {
                console.log('No parameters set, skipping fetch.');
                return;
            }
            try {
                const params = new URLSearchParams({
                    years: years.join(','),
                    athletes: selectedAthletes.map((athlete) => athlete.athlete_id).join(','),
                });

                const data = await apiRequest(`/map/?${params.toString()}`);
                if (data) {
                    setRoutesData(data || []);
                    displayRoutes(data, mapRef.current, selectedAthletes, highlightedRoutesGroupRef.current, isZoomingRef);
                }
            } catch (error) {
                setRoutesData([]); // Fallback to an empty state
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
                mapRef.current.remove();
                mapRef.current = null;

            }
        };
    }, [years, selectedAthletes]);

    return (
        <StyledMap id="map" />
    );
};

const isMobile = window.matchMedia("(max-width: 1000px)").matches;

const displayRoutes = (data, map, selectedAthletes, highlightedRoutesGroup, isZoomingRef) => {
    highlightedRoutesGroup.clearLayers();

    let allBounds = [];
    const batchSize = 20;
    let index = 0;

    const processNextBatch = () => {
        const batch = data.slice(index, index + batchSize);
        batch.forEach(activity => {
            const athleteColor =
                selectedAthletes.find(a => a.athlete_id.toString() === activity.athlete_id.toString())?.color || 'red';

            if (activity.summary_polyline && activity.summary_polyline.coordinates.length > 1) {
                const latLngs = activity.summary_polyline.coordinates.map(([lng, lat]) => [lat, lng]); // Flip coordinates

                const routePolyline = L.polyline(latLngs, {
                    color: athleteColor,
                    opacity: 1,
                    weight: 2,
                }).addTo(map);

                if (!isMobile) {
                    const interactionPolyline = L.polyline(latLngs, {
                        color: 'transparent',
                        opacity: 0,
                        weight: 10, // Increase weight for the interaction area
                    }).addTo(map);

                    attachEventsToPolyline(interactionPolyline, routePolyline, activity, map, highlightedRoutesGroup, isZoomingRef);
                } else {
                    attachEventsToPolyline(routePolyline, routePolyline, activity, map, highlightedRoutesGroup, isZoomingRef); // Use the original polyline
                }

                allBounds.push(routePolyline.getBounds());
            }
        });

        index += batchSize;

        if (index < data.length) {
            requestAnimationFrame(processNextBatch);
        } else {
            if (allBounds.length > 0) {
                const combinedBounds = allBounds.reduce((acc, bounds) => acc.extend(bounds), L.latLngBounds(allBounds[0]));
                map.fitBounds(combinedBounds);
            }
        }
    };

    processNextBatch();
};

const attachEventsToPolyline = (polyline, routePolyline, activity, map, highlightedRoutesGroup, isZoomingRef) => {
    polyline.on('mouseover', () => {
        if (!isZoomingRef.current) {
            const highlightedCopy = L.polyline(routePolyline.getLatLngs(), {
                color: '#fff',
                opacity: 1,
                weight: 5,
            }).addTo(highlightedRoutesGroup);

            const polylineElement = highlightedCopy._path;
            if (polylineElement) {
                polylineElement.style.pointerEvents = 'none';
            }
            routePolyline._highlightedCopy = highlightedCopy;
        }
    });

    polyline.on('mouseout', () => {
        if (routePolyline._highlightedCopy) {
            highlightedRoutesGroup.removeLayer(routePolyline._highlightedCopy);
            delete routePolyline._highlightedCopy;
        }
    });

    polyline.on('click', function (e) {
        const distance = parseFloat(activity.distance).toFixed(2);
        const movingTime = parseFloat(activity.moving_time).toFixed(2);

        const popupContent = `
            <strong>Activity Name:</strong> ${activity.name}<br>
            <strong>Distance:</strong> ${distance} km<br>
            <strong>Moving-Time:</strong> ${movingTime} min<br>
            <a href="${activity.url}" target="_blank">View Activity</a>
        `;

         L.popup()
            .setLatLng(e.latlng)
            .setContent(popupContent)
            .openOn(map);
    });
};

