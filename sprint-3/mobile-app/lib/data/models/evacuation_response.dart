import 'geojson_geometry.dart';

class EvacuationResponse {
  const EvacuationResponse({
    required this.originLatitude,
    required this.originLongitude,
    required this.calculatedAt,
    required this.verticalEvacuation,
    required this.emergencyMessage,
    required this.sarAlert,
    required this.routes,
  });

  final double originLatitude;
  final double originLongitude;
  final DateTime calculatedAt;
  final bool verticalEvacuation;
  final String? emergencyMessage;
  final bool sarAlert;
  final List<EvacuationRoute> routes;

  factory EvacuationResponse.fromJson(Map<String, dynamic> json) {
    final origin = json['asal'] as Map<String, dynamic>;
    return EvacuationResponse(
      originLatitude: (origin['lat'] as num).toDouble(),
      originLongitude: (origin['lng'] as num).toDouble(),
      calculatedAt: DateTime.parse(json['dihitung_pada'] as String),
      verticalEvacuation: json['evakuasi_vertikal'] as bool,
      emergencyMessage: json['pesan_darurat'] as String?,
      sarAlert: json['alert_sar'] as bool,
      routes: (json['rute'] as List<dynamic>? ?? const [])
          .map((item) => EvacuationRoute.fromJson(item as Map<String, dynamic>))
          .toList(growable: false),
    );
  }
}

class EvacuationRoute {
  const EvacuationRoute({
    required this.id,
    required this.rwId,
    required this.primary,
    required this.distanceMeters,
    required this.estimatedMinutes,
    required this.status,
    required this.loadPercent,
    required this.segments,
    required this.geometry,
  });

  final String id;
  final String rwId;
  final bool primary;
  final int distanceMeters;
  final int estimatedMinutes;
  final String status;
  final double loadPercent;
  final List<RouteSegment> segments;
  final GeoJsonGeometry geometry;

  factory EvacuationRoute.fromJson(Map<String, dynamic> json) {
    return EvacuationRoute(
      id: json['id'] as String,
      rwId: json['rw_id'] as String,
      primary: json['utama'] as bool,
      distanceMeters: (json['jarak_m'] as num).toInt(),
      estimatedMinutes: (json['estimasi_menit'] as num).toInt(),
      status: json['status'] as String,
      loadPercent: (json['beban_persen'] as num).toDouble(),
      segments: (json['segmen_dilalui'] as List<dynamic>? ?? const [])
          .map((item) => RouteSegment.fromJson(item as Map<String, dynamic>))
          .toList(growable: false),
      geometry: GeoJsonGeometry.fromJson(
        json['geometri'] as Map<String, dynamic>,
      ),
    );
  }
}

class RouteSegment {
  const RouteSegment({
    required this.segmentId,
    required this.rwId,
    required this.geometry,
    required this.lengthMeters,
    required this.capacity,
    required this.activeUsers,
    required this.status,
    required this.manuallyBlocked,
    required this.reason,
  });

  final String segmentId;
  final String rwId;
  final GeoJsonGeometry geometry;
  final double lengthMeters;
  final int capacity;
  final int activeUsers;
  final String status;
  final bool manuallyBlocked;
  final String reason;

  factory RouteSegment.fromJson(Map<String, dynamic> json) {
    return RouteSegment(
      segmentId: json['segment_id'] as String,
      rwId: json['rw_id'] as String,
      geometry: GeoJsonGeometry.fromJson(
        json['geometri'] as Map<String, dynamic>,
      ),
      lengthMeters: (json['panjang_m'] as num).toDouble(),
      capacity: (json['kapasitas_maks'] as num).toInt(),
      activeUsers: (json['pengguna_aktif'] as num).toInt(),
      status: json['status'] as String,
      manuallyBlocked: json['diblokir_manual'] as bool,
      reason: json['alasan'] as String,
    );
  }
}
