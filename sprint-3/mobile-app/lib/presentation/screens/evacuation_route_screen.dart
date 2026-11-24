// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/evacuation_response.dart';
import '../../data/models/hazard_response.dart';
import '../../data/models/navigation_session.dart';
import '../widgets/hazard_map_layers.dart';
import '../widgets/stale_data_banner.dart';

class EvacuationRouteScreen extends ConsumerWidget {
  const EvacuationRouteScreen({
    super.key,
    required this.session,
    required this.hazards,
  });

  final NavigationSession session;
  final HazardResponse? hazards;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final response = session.response;
    final routes = response.routes;
    final center = session.origin;

    return Scaffold(
      backgroundColor: const Color(0xFFF3F6FA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text(
          'Rute Evakuasi',
          style: TextStyle(
            color: Color(0xFF132238),
            fontSize: 17,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: Stack(
        children: [
          FlutterMap(
            options: MapOptions(initialCenter: center, initialZoom: 15),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.hyperevac.warga',
                maxZoom: 19,
              ),
              PolygonLayer(polygons: buildHazardPolygons(hazards)),
              PolylineLayer(polylines: buildRoutePolylines(response)),
              MarkerLayer(markers: buildHazardMarkers(hazards, center)),
              RichAttributionWidget(
                attributions: const [
                  TextSourceAttribution('© OpenStreetMap contributors'),
                ],
              ),
            ],
          ),
          DraggableScrollableSheet(
            initialChildSize: 0.48,
            minChildSize: 0.34,
            maxChildSize: 0.85,
            snap: true,
            snapSizes: const [0.48, 0.85],
            builder: (context, scrollController) {
              return Material(
                color: Colors.white,
                elevation: 18,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(24),
                ),
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.fromLTRB(18, 10, 18, 26),
                  children: [
                    Center(
                      child: Container(
                        width: 42,
                        height: 4,
                        decoration: BoxDecoration(
                          color: const Color(0xFFD0D8E2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                    const SizedBox(height: 15),
                    const Text(
                      'PILIH JALUR AMAN',
                      style: TextStyle(
                        color: Color(0xFF536579),
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Dihitung ${_formatTime(response.calculatedAt)} · '
                      '${routes.length} pilihan rute',
                      style: const TextStyle(
                        color: Color(0xFF132238),
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 11),
                    StaleDataBanner(
                      dataExpired: hazards?.dataKedaluwarsa ?? false,
                    ),
                    if (routes.isEmpty)
                      const _RouteWarning(
                        icon: Icons.route_outlined,
                        title: 'Rute darat tidak tersedia',
                        detail:
                            'Jangan memasuki ruas yang ditutup. Ikuti arahan petugas di lokasi.',
                      )
                    else
                      for (final route in routes)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: _RouteCard(route: route),
                        ),
                    const SizedBox(height: 3),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEAF2FA),
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: const Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            Icons.info_outline_rounded,
                            color: Color(0xFF315D85),
                            size: 19,
                          ),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Ikuti petunjuk petugas dan kondisi aktual di lapangan. '
                              'Jangan melintasi ruas yang tertutup meskipun terlihat dapat dilewati.',
                              style: TextStyle(
                                color: Color(0xFF315D85),
                                fontSize: 11,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _RouteCard extends StatelessWidget {
  const _RouteCard({required this.route});

  final EvacuationRoute route;

  @override
  Widget build(BuildContext context) {
    final primary = route.primary;
    final load = route.loadPercent;
    final loadColor = load >= 90
        ? const Color(0xFFB42318)
        : load >= 70
        ? const Color(0xFFB54708)
        : const Color(0xFF087F5B);
    final bottleneck = load >= 90
        ? 'PADAT · gunakan alternatif bila aman'
        : load >= 70
        ? 'MENINGKAT · waspadai antrean'
        : 'LANCAR · anti-bottleneck aktif';

    return Container(
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: primary ? const Color(0xFFF0F7FF) : const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: primary ? const Color(0xFF9BC7F2) : const Color(0xFFD9E1EA),
          width: primary ? 1.5 : 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: primary
                      ? const Color(0xFFDCEEFF)
                      : const Color(0xFFE8EDF3),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  primary ? Icons.route_rounded : Icons.alt_route_rounded,
                  color: primary
                      ? const Color(0xFF145DA0)
                      : const Color(0xFF536579),
                  size: 19,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      primary ? 'Rute Utama' : 'Rute Alternatif',
                      style: const TextStyle(
                        color: Color(0xFF132238),
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    Text(
                      '${route.status} · ${route.distanceMeters} m',
                      style: const TextStyle(
                        color: Color(0xFF536579),
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '${route.estimatedMinutes} mnt',
                style: const TextStyle(
                  color: Color(0xFF132238),
                  fontSize: 15,
                  fontWeight: FontWeight.w900,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              const Text(
                'Beban jalur',
                style: TextStyle(color: Color(0xFF536579), fontSize: 11),
              ),
              const Spacer(),
              Text(
                '${load.toStringAsFixed(1)}%',
                style: TextStyle(
                  color: loadColor,
                  fontSize: 12,
                  fontWeight: FontWeight.w900,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: (load / 100).clamp(0.0, 1.0).toDouble(),
              minHeight: 8,
              backgroundColor: const Color(0xFFE1E7EF),
              valueColor: AlwaysStoppedAnimation(loadColor),
            ),
          ),
          const SizedBox(height: 9),
          Row(
            children: [
              Icon(
                load >= 90
                    ? Icons.warning_amber_rounded
                    : Icons.verified_user_outlined,
                color: loadColor,
                size: 16,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  bottleneck,
                  style: TextStyle(
                    color: loadColor,
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              Text(
                '${route.segments.length} ruas',
                style: const TextStyle(color: Color(0xFF536579), fontSize: 10),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RouteWarning extends StatelessWidget {
  const _RouteWarning({
    required this.icon,
    required this.title,
    required this.detail,
  });

  final IconData icon;
  final String title;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFE6E6),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFF3B4B4)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFFB42318)),
          const SizedBox(width: 9),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Color(0xFF8F1D1D),
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  detail,
                  style: const TextStyle(
                    color: Color(0xFF8F1D1D),
                    fontSize: 11,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

String _formatTime(DateTime value) {
  final local = value.toLocal();
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '$hour:$minute';
}
