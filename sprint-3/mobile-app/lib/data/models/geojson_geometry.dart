import 'package:latlong2/latlong.dart';

class GeoJsonGeometry {
  const GeoJsonGeometry({required this.type, required this.coordinates});

  final String type;
  final Object? coordinates;

  factory GeoJsonGeometry.fromJson(Map<String, dynamic> json) {
    return GeoJsonGeometry(
      type: json['type'] as String? ?? '',
      coordinates: json['coordinates'],
    );
  }

  LatLng? get point {
    if (type != 'Point' || coordinates is! List) return null;
    return _latLng(coordinates! as List);
  }

  List<LatLng> get lineString {
    if (type != 'LineString' || coordinates is! List) return const [];
    return (coordinates! as List)
        .whereType<List>()
        .map(_latLng)
        .whereType<LatLng>()
        .toList(growable: false);
  }

  List<List<LatLng>> get polygonRings {
    final result = <List<LatLng>>[];
    if (type == 'Polygon' && coordinates is List) {
      for (final ring in coordinates! as List) {
        if (ring is List) result.add(_ring(ring));
      }
    } else if (type == 'MultiPolygon' && coordinates is List) {
      for (final polygon in coordinates! as List) {
        if (polygon is! List) continue;
        for (final ring in polygon) {
          if (ring is List) result.add(_ring(ring));
        }
      }
    }
    return result.where((ring) => ring.length >= 3).toList(growable: false);
  }

  List<LatLng> _ring(List<dynamic> coordinates) {
    return coordinates
        .whereType<List>()
        .map(_latLng)
        .whereType<LatLng>()
        .toList(growable: false);
  }

  LatLng? _latLng(List<dynamic> coordinates) {
    if (coordinates.length < 2 ||
        coordinates[0] is! num ||
        coordinates[1] is! num) {
      return null;
    }
    return LatLng(
      (coordinates[1] as num).toDouble(),
      (coordinates[0] as num).toDouble(),
    );
  }
}
