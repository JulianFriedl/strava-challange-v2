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


export default function MapDisplay({ years, selectedAthletes, onLoadComplete}) {
    const [, setRoutesData] = useState([]);
    const mapRef = useRef(null);
    const routesGroupRef = useRef(null);
    const highlightedRoutesGroupRef = useRef(null);
    const isZoomingRef = useRef(false); // Ref to track zooming state
    const cancelDrawingRef = useRef(false);

    // Initialize the map once
    useEffect(() => {
        if (!mapRef.current) {
            const map = L.map('map', {
                center: [0, 0],
                zoom: 3,
                maxZoom: 22,
                minZoom: 3,
                maxBounds: [[-90, -180], [90, 180]],
                maxBoundsViscosity: 1.0,
            });

            routesGroupRef.current = L.layerGroup().addTo(map);

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

            mapRef.current = map;
        }
    }, []);

    useEffect(() => {
      // Clear all existing map layers (routes and highlights)
      if (mapRef.current && highlightedRoutesGroupRef.current) {
          routesGroupRef.current.clearLayers();
          highlightedRoutesGroupRef.current.clearLayers();
      }
       const fetchDataAndDraw = async () => {
            if (years.length === 0 || selectedAthletes.length === 0) {
                // console.log('No parameters set, skipping fetch.');
                onLoadComplete();
                return;
            }

            try {
                const params = new URLSearchParams({
                    years: years.join(','),
                    athletes: selectedAthletes.map((athlete) => athlete.athlete_id).join(','),
                });

                const data = await apiRequest(`/map/?${params.toString()}`);
                if (data) {
                    cancelDrawingRef.current = false;
                    setRoutesData(data || []);
                    await displayRoutes(
                        data,
                        mapRef.current,
                        selectedAthletes,
                        highlightedRoutesGroupRef.current,
                        isZoomingRef,
                        cancelDrawingRef,
                        routesGroupRef.current
                    );
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                setRoutesData([]);
            } finally {
                onLoadComplete();
            }
        };

        fetchDataAndDraw();

        return () => {
            cancelDrawingRef.current = true;
        };
    }, [years, selectedAthletes]);

    return <StyledMap id="map" />;
}

const isMobile = window.matchMedia("(max-width: 1000px)").matches;

const displayRoutes = (data, map, selectedAthletes, highlightedRoutesGroup, isZoomingRef, cancelDrawingRef, routesGroup) => {

   if (!data || data.length === 0) {
        console.warn('No valid data to display.');
        return;
    }
    highlightedRoutesGroup.clearLayers();

    let allBounds = [];
    const batchSize = 20;
    let index = 0;

    const processNextBatch = () => {
        if (cancelDrawingRef.current) {
            // console.log('Drawing canceled.');
            return;
        }
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
                }).addTo(routesGroup);

                if (!isMobile) {
                    const interactionPolyline = L.polyline(latLngs, {
                        color: 'transparent',
                        opacity: 0,
                        weight: 10, // Increase weight for the interaction area
                    }).addTo(routesGroup);

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

