// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../data/models/evacuation_response.dart';
import '../../data/models/hazard_response.dart';

Color hazardColor(String level) {
  return switch (level) {
    'WASPADA' => const Color(0xFFFFC107),
    'SIAGA' => const Color(0xFFFF7A00),
    'AWAS' => const Color(0xFFE53935),
    _ => const Color(0xFF2E7D32),
  };
}

List<Polygon> buildHazardPolygons(HazardResponse? response) {
  if (response == null) return const [];
  return [
    for (final hazard in response.hazards)
      for (final ring in hazard.geometri.polygonRings)
        Polygon(
          points: ring,
          color: hazardColor(hazard.levelBahaya).withValues(alpha: 0.23),
          borderColor: hazardColor(hazard.levelBahaya),
          borderStrokeWidth: 3,
        ),
  ];
}

List<Marker> buildHazardMarkers(HazardResponse? response, LatLng? origin) {
  final markers = <Marker>[];
  final meetingPoint = response?.rw.titikKumpul.point;
  if (meetingPoint != null) {
    markers.add(
      Marker(
        point: meetingPoint,
        width: 52,
        height: 58,
        child: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.flag_rounded, color: Color(0xFF087F5B), size: 32),
            Text(
              'TITIK KUMPUL',
              style: TextStyle(
                color: Color(0xFF143C2E),
                fontSize: 8,
                fontWeight: FontWeight.w900,
                shadows: [Shadow(color: Colors.white, blurRadius: 4)],
              ),
            ),
          ],
        ),
      ),
    );
  }
  if (origin != null) {
    markers.add(
      Marker(
        point: origin,
        width: 32,
        height: 32,
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF1565C0),
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 3),
            boxShadow: const [
              BoxShadow(color: Color(0x55000000), blurRadius: 6),
            ],
          ),
        ),
      ),
    );
  }
  return markers;
}

List<Polyline> buildRoutePolylines(EvacuationResponse? response) {
  if (response == null) return const [];
  return [
    for (final route in response.routes)
      if (route.geometry.lineString.length >= 2)
        Polyline(
          points: route.geometry.lineString,
          color: route.primary
              ? const Color(0xFF087F5B)
              : const Color(0xFF64748B),
          strokeWidth: route.primary ? 7 : 5,
          borderColor: Colors.white,
          borderStrokeWidth: route.primary ? 1.5 : 1,
          pattern: route.primary
              ? const StrokePattern.solid()
              : StrokePattern.dashed(segments: [9, 7]),
        ),
  ];
}
