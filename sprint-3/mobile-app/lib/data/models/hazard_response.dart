import 'geojson_geometry.dart';

class HazardResponse {
  const HazardResponse({
    required this.rw,
    required this.dataDiperbarui,
    required this.dataKedaluwarsa,
    required this.hazards,
  });

  final RwHazardInfo rw;
  final DateTime dataDiperbarui;
  final bool dataKedaluwarsa;
  final List<HazardItem> hazards;

  factory HazardResponse.fromJson(Map<String, dynamic> json) {
    return HazardResponse(
      rw: RwHazardInfo.fromJson(json['rw'] as Map<String, dynamic>),
      dataDiperbarui: DateTime.parse(json['data_diperbarui'] as String),
      dataKedaluwarsa: json['data_kedaluwarsa'] as bool? ?? false,
      hazards: (json['hazards'] as List<dynamic>? ?? const [])
          .map((item) => HazardItem.fromJson(item as Map<String, dynamic>))
          .toList(growable: false),
    );
  }
}

class RwHazardInfo {
  const RwHazardInfo({
    required this.id,
    required this.namaRw,
    required this.batasWilayah,
    required this.titikKumpul,
  });

  final String id;
  final String namaRw;
  final GeoJsonGeometry batasWilayah;
  final GeoJsonGeometry titikKumpul;

  factory RwHazardInfo.fromJson(Map<String, dynamic> json) {
    return RwHazardInfo(
      id: json['id'] as String,
      namaRw: json['nama_rw'] as String,
      batasWilayah: GeoJsonGeometry.fromJson(
        json['batas_wilayah'] as Map<String, dynamic>,
      ),
      titikKumpul: GeoJsonGeometry.fromJson(
        json['titik_kumpul'] as Map<String, dynamic>,
      ),
    );
  }
}

class HazardItem {
  const HazardItem({
    required this.id,
    required this.rwId,
    required this.sumber,
    required this.jenis,
    required this.levelBahaya,
    required this.tingkatBahaya,
    required this.geometri,
    required this.waktuData,
    required this.terverifikasi,
  });

  final String id;
  final String rwId;
  final String sumber;
  final String jenis;
  final String levelBahaya;
  final double tingkatBahaya;
  final GeoJsonGeometry geometri;
  final DateTime waktuData;
  final bool terverifikasi;

  factory HazardItem.fromJson(Map<String, dynamic> json) {
    return HazardItem(
      id: json['id'] as String,
      rwId: json['rw_id'] as String,
      sumber: json['sumber'] as String,
      jenis: json['jenis'] as String,
      levelBahaya: json['level_bahaya'] as String,
      tingkatBahaya: (json['tingkat_bahaya'] as num).toDouble(),
      geometri: GeoJsonGeometry.fromJson(
        json['geometri'] as Map<String, dynamic>,
      ),
      waktuData: DateTime.parse(json['waktu_data'] as String),
      terverifikasi: json['terverifikasi'] as bool,
    );
  }
}
