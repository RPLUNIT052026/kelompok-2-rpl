class RoadReportPayload {
  const RoadReportPayload({
    required this.deviceId,
    required this.segmentId,
    required this.type,
    required this.latitude,
    required this.longitude,
    required this.note,
    required this.createdAt,
  });

  final String deviceId;
  final String segmentId;
  final String type;
  final double latitude;
  final double longitude;
  final String note;
  final DateTime createdAt;

  Map<String, dynamic> toJson() => {
    'device_id': deviceId,
    'segment_id': segmentId,
    'tipe': type,
    'lat': latitude,
    'lng': longitude,
    'catatan': note,
    'dibuat_pada': createdAt.toUtc().toIso8601String(),
  };

  factory RoadReportPayload.fromJson(Map<String, dynamic> json) {
    return RoadReportPayload(
      deviceId: json['device_id'] as String,
      segmentId: json['segment_id'] as String,
      type: json['tipe'] as String,
      latitude: (json['lat'] as num).toDouble(),
      longitude: (json['lng'] as num).toDouble(),
      note: json['catatan'] as String? ?? '',
      createdAt: DateTime.parse(json['dibuat_pada'] as String).toUtc(),
    );
  }
}
