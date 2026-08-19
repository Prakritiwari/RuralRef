import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Ambulance, MapPin, Navigation, Clock, ShieldCheck } from "lucide-react";

export default function InteractiveTrackingMap({
  phcLocation,
  hospitalLocation,
  ambulanceLocation,
  trail = [],
  height = "380px",
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef({});
  const polylineRef = useRef(null);
  const trailPolylineRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize Map if not already created
    if (!mapInstanceRef.current) {
      const initialLat = phcLocation?.latitude || ambulanceLocation?.latitude || 19.6967;
      const initialLng = phcLocation?.longitude || ambulanceLocation?.longitude || 72.7699;

      const map = L.map(mapContainerRef.current, {
        center: [initialLat, initialLng],
        zoom: 11,
        zoomControl: true,
      });

      // OpenStreetMap Free Tile Layer
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    const bounds = [];

    // Helper to create styled HTML div icons
    const createCustomIcon = (bgColor, iconHtml, pulse = false) => {
      return L.divIcon({
        className: "custom-map-marker",
        html: `
          <div style="
            position: relative;
            background: ${bgColor};
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.3);
            border: 2px solid white;
          ">
            ${pulse ? '<div class="marker-pulse-ring" style="position:absolute;inset:-6px;border-radius:50%;border:2px solid ' + bgColor + ';animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>' : ''}
            ${iconHtml}
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -20],
      });
    };

    // 1. PHC Marker
    if (phcLocation?.latitude && phcLocation?.longitude) {
      const phcLatLng = [phcLocation.latitude, phcLocation.longitude];
      bounds.push(phcLatLng);

      if (!markersRef.current.phc) {
        const phcIcon = createCustomIcon("#16a34a", "🏥");
        markersRef.current.phc = L.marker(phcLatLng, { icon: phcIcon })
          .addTo(map)
          .bindPopup(`<b>${phcLocation.name || "PHC Location"}</b><br/>Pickup Origin`);
      } else {
        markersRef.current.phc.setLatLng(phcLatLng);
      }
    }

    // 2. Hospital Marker
    if (hospitalLocation?.latitude && hospitalLocation?.longitude) {
      const hospLatLng = [hospitalLocation.latitude, hospitalLocation.longitude];
      bounds.push(hospLatLng);

      if (!markersRef.current.hospital) {
        const hospIcon = createCustomIcon("#2563eb", "🏨");
        markersRef.current.hospital = L.marker(hospLatLng, { icon: hospIcon })
          .addTo(map)
          .bindPopup(`<b>${hospitalLocation.name || "Hospital Destination"}</b><br/>Receiving Facility`);
      } else {
        markersRef.current.hospital.setLatLng(hospLatLng);
      }
    }

    // 3. Ambulance Live Marker
    if (ambulanceLocation?.latitude && ambulanceLocation?.longitude) {
      const ambLatLng = [ambulanceLocation.latitude, ambulanceLocation.longitude];
      bounds.push(ambLatLng);

      if (!markersRef.current.ambulance) {
        const ambIcon = createCustomIcon("#dc2626", "🚑", true);
        markersRef.current.ambulance = L.marker(ambLatLng, { icon: ambIcon, zIndexOffset: 1000 })
          .addTo(map)
          .bindPopup(`<b>Ambulance: ${ambulanceLocation.vehicle_number || "Emergency Unit"}</b><br/>Status: ${ambulanceLocation.status || "En Route"}`);
      } else {
        markersRef.current.ambulance.setLatLng(ambLatLng);
        markersRef.current.ambulance.setPopupContent(
          `<b>Ambulance: ${ambulanceLocation.vehicle_number || "Emergency Unit"}</b><br/>Status: ${ambulanceLocation.status || "En Route"}`
        );
      }
    }

    // 4. Draw Route Connecting Line
    if (phcLocation?.latitude && hospitalLocation?.latitude) {
      const routePoints = [
        [phcLocation.latitude, phcLocation.longitude],
        [hospitalLocation.latitude, hospitalLocation.longitude],
      ];

      if (!polylineRef.current) {
        polylineRef.current = L.polyline(routePoints, {
          color: "#2563eb",
          weight: 3,
          opacity: 0.6,
          dashArray: "6, 8",
        }).addTo(map);
      } else {
        polylineRef.current.setLatLngs(routePoints);
      }
    }

    // 5. Draw GPS Telemetry Trail if points exist
    if (trail && trail.length > 1) {
      const trailPoints = trail.map((p) => [p.latitude, p.longitude]);
      if (!trailPolylineRef.current) {
        trailPolylineRef.current = L.polyline(trailPoints, {
          color: "#dc2626",
          weight: 4,
          opacity: 0.85,
        }).addTo(map);
      } else {
        trailPolylineRef.current.setLatLngs(trailPoints);
      }
    }

    // Fit map view smoothly to contain all markers
    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    }
  }, [phcLocation, hospitalLocation, ambulanceLocation, trail]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="map-wrapper" style={{ position: "relative", width: "100%", borderRadius: "14px", overflow: "hidden", border: "1px solid var(--line)", background: "#e2e8f0" }}>
      {/* Map Canvas */}
      <div ref={mapContainerRef} style={{ width: "100%", height }} />

      {/* Floating Status Overlay */}
      {ambulanceLocation && (
        <div
          className="map-overlay-card"
          style={{
            position: "absolute",
            bottom: "16px",
            left: "16px",
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(6px)",
            padding: "12px 16px",
            borderRadius: "10px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
            zIndex: 1000,
            display: "flex",
            flexDirection: "column",
            gap: "4px",
            fontSize: "12px",
            border: "1px solid var(--line)",
            maxWidth: "280px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: "700", color: "#1e293b" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 0 3px #dcfce7" }} />
            <span>{ambulanceLocation.vehicle_number || "Ambulance Unit"}</span>
          </div>

          <div style={{ color: "#64748b", fontSize: "11px" }}>
            Status: <b style={{ color: "#2563eb" }}>{String(ambulanceLocation.status || "").replace(/_/g, " ")}</b>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#475569", marginTop: "4px", fontSize: "10.5px" }}>
            <Navigation size={13} />
            <span>
              {Number(ambulanceLocation.latitude).toFixed(4)}, {Number(ambulanceLocation.longitude).toFixed(4)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
