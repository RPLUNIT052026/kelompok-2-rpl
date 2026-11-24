// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../core/api_client.dart';
import '../../core/config.dart';
import '../../core/providers.dart';
import '../../data/models/hazard_response.dart';
import '../../data/models/navigation_session.dart';
import '../widgets/hazard_map_layers.dart';
import '../widgets/offline_queue_badge.dart';
import '../widgets/sos_report_modal.dart';
import '../widgets/stale_data_banner.dart';
import 'evacuation_route_screen.dart';
import 'vertical_evacuation_screen.dart';

class HazardMapScreen extends ConsumerStatefulWidget {
  const HazardMapScreen({super.key});

  @override
  ConsumerState<HazardMapScreen> createState() => _HazardMapScreenState();
}

class _HazardMapScreenState extends ConsumerState<HazardMapScreen> {
  bool _findingRoute = false;
  bool _openingSos = false;
  NavigationSession? _lastSession;

  Future<LatLng> _getCurrentPosition() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      throw StateError('Aktifkan layanan lokasi untuk mencari rute evakuasi.');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied) {
      throw StateError(
        'Izin lokasi diperlukan untuk menentukan rute evakuasi.',
      );
    }
    if (permission == LocationPermission.deniedForever) {
      throw StateError(
        'Izin lokasi ditolak permanen. Aktifkan melalui Pengaturan perangkat.',
      );
    }

    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 15),
      ),
    );
    return LatLng(position.latitude, position.longitude);
  }

  Future<NavigationSession> _loadNavigationSession() async {
    final origin = await _getCurrentPosition();
    final response = await ref
        .read(routeRepositoryProvider)
        .getEvacuationRoutes(
          latitude: origin.latitude,
          longitude: origin.longitude,
        );
    final session = NavigationSession(origin: origin, response: response);
    _lastSession = session;
    return session;
  }

  Future<void> _findRoute() async {
    setState(() => _findingRoute = true);
    try {
      final session = await _loadNavigationSession();
      if (!mounted) return;
      final screen = session.response.verticalEvacuation
          ? VerticalEvacuationScreen(
              message: session.response.emergencyMessage ?? '',
              sarAlertSent: session.response.sarAlert,
              dataExpired:
                  ref.read(hazardsProvider).valueOrNull?.dataKedaluwarsa ??
                  false,
            )
          : EvacuationRouteScreen(
              session: session,
              hazards: ref.read(hazardsProvider).valueOrNull,
            );
      await Navigator.of(
        context,
      ).push(MaterialPageRoute<void>(builder: (_) => screen));
    } catch (error) {
      if (mounted) _showMessage(apiErrorMessage(error));
    } finally {
      if (mounted) setState(() => _findingRoute = false);
    }
  }

  Future<void> _openSos() async {
    setState(() => _openingSos = true);
    try {
      final position = await _getCurrentPosition();
      final deviceId = await ref.read(deviceIdProvider.future);
      if (!mounted) return;
      final segments = _lastSession?.reportableSegments ?? const [];
      await showModalBottomSheet<bool>(
        context: context,
        isScrollControlled: true,
        useSafeArea: true,
        backgroundColor: Colors.white,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        builder: (_) => SosReportModal(
          deviceId: deviceId,
          position: position,
          segments: segments,
        ),
      );
    } catch (error) {
      if (mounted) _showMessage(apiErrorMessage(error));
    } finally {
      if (mounted) setState(() => _openingSos = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(behavior: SnackBarBehavior.floating, content: Text(message)),
      );
  }

  @override
  Widget build(BuildContext context) {
    final hazardAsync = ref.watch(hazardsProvider);
    final registrationAsync = ref.watch(deviceRegistrationProvider);
    final hazardData = hazardAsync.valueOrNull;
    const center = LatLng(
      AppConfig.fallbackLatitude,
      AppConfig.fallbackLongitude,
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF3F6FA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        titleSpacing: 16,
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'HYPEREVAC',
              style: TextStyle(
                color: Color(0xFF132238),
                fontSize: 14,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.1,
              ),
            ),
            SizedBox(height: 1),
            Text(
              'PANDUAN EVAKUASI WARGA',
              style: TextStyle(
                color: Color(0xFF536579),
                fontSize: 9,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.65,
              ),
            ),
          ],
        ),
        actions: [
          const OfflineQueueBadge(),
          const SizedBox(width: 8),
          IconButton(
            tooltip: 'Muat ulang peta bahaya',
            onPressed: () => ref.invalidate(hazardsProvider),
            icon: const Icon(Icons.refresh_rounded),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: Stack(
        children: [
          FlutterMap(
            options: MapOptions(
              initialCenter: center,
              initialZoom: 14,
              maxZoom: 19,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.hyperevac.warga',
                maxZoom: 19,
              ),
              PolygonLayer(polygons: buildHazardPolygons(hazardData)),
              MarkerLayer(markers: buildHazardMarkers(hazardData, null)),
              RichAttributionWidget(
                attributions: const [
                  TextSourceAttribution('© OpenStreetMap contributors'),
                ],
              ),
            ],
          ),
          DraggableScrollableSheet(
            initialChildSize: 0.43,
            minChildSize: 0.34,
            maxChildSize: 0.82,
            snap: true,
            snapSizes: const [0.43, 0.82],
            builder: (context, scrollController) {
              return Material(
                color: Colors.white,
                elevation: 18,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(24),
                ),
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.fromLTRB(18, 10, 18, 24),
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
                    const SizedBox(height: 14),
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                hazardData?.rw.namaRw ?? 'Peta wilayah',
                                style: const TextStyle(
                                  color: Color(0xFF132238),
                                  fontSize: 20,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                hazardData == null
                                    ? 'Memuat informasi bahaya…'
                                    : '${hazardData.hazards.length} zona bahaya aktif · WGS 84',
                                style: const TextStyle(
                                  color: Color(0xFF536579),
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        _HazardStatusBadge(hazards: hazardData),
                      ],
                    ),
                    const SizedBox(height: 14),
                    StaleDataBanner(
                      dataExpired: hazardData?.dataKedaluwarsa ?? false,
                      serviceUnavailable:
                          hazardAsync.hasError && hazardData == null,
                    ),
                    if (hazardAsync.hasError && hazardData == null)
                      _InlineWarning(
                        message: apiErrorMessage(hazardAsync.error!),
                        actionLabel: 'Coba lagi',
                        onAction: () => ref.invalidate(hazardsProvider),
                      ),
                    if (registrationAsync.hasError)
                      _InlineWarning(
                        message:
                            'Perangkat belum terdaftar: ${apiErrorMessage(registrationAsync.error!)}',
                        actionLabel: 'Daftar ulang',
                        onAction: () =>
                            ref.invalidate(deviceRegistrationProvider),
                      ),
                    if (hazardData != null) ...[
                      const Text(
                        'TINGKAT BAHAYA',
                        style: TextStyle(
                          color: Color(0xFF536579),
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.7,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 7,
                        children: [
                          for (final hazard in hazardData.hazards)
                            _HazardChip(
                              level: hazard.levelBahaya,
                              label:
                                  '${hazard.levelBahaya} · ${hazard.jenis.replaceAll('_', ' ')}',
                            ),
                          if (hazardData.hazards.isEmpty)
                            const _HazardChip(
                              level: 'AMAN',
                              label: 'Tidak ada bahaya aktif',
                            ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 15),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(
                          Icons.flag_circle_rounded,
                          color: Color(0xFF087F5B),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            hazardData == null
                                ? 'Titik kumpul akan tampil saat data wilayah termuat.'
                                : 'Titik kumpul aman: ${hazardData.rw.namaRw}. Ikuti jalur yang direkomendasikan aplikasi.',
                            style: const TextStyle(
                              color: Color(0xFF344054),
                              fontSize: 12,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 58,
                      child: FilledButton.icon(
                        onPressed: _findingRoute || _openingSos
                            ? null
                            : _findRoute,
                        icon: _findingRoute
                            ? const SizedBox(
                                width: 21,
                                height: 21,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.route_rounded, size: 23),
                        label: Text(
                          _findingRoute
                              ? 'Menentukan lokasi & rute…'
                              : 'Cari Rute Evakuasi',
                        ),
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF145DA0),
                          foregroundColor: Colors.white,
                          textStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(13),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 9),
                    SizedBox(
                      height: 56,
                      child: OutlinedButton.icon(
                        onPressed: _findingRoute || _openingSos
                            ? null
                            : _openSos,
                        icon: _openingSos
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.sos_rounded, size: 23),
                        label: Text(
                          _openingSos
                              ? 'Membuka laporan…'
                              : 'Kirim Laporan SOS',
                        ),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFB42318),
                          side: const BorderSide(
                            color: Color(0xFFB42318),
                            width: 1.5,
                          ),
                          textStyle: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(13),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'Jika rute darat tidak tersedia, ikuti instruksi evakuasi vertikal dan arahan petugas.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Color(0xFF667085),
                        fontSize: 11,
                        height: 1.4,
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

class _HazardStatusBadge extends StatelessWidget {
  const _HazardStatusBadge({required this.hazards});

  final HazardResponse? hazards;

  @override
  Widget build(BuildContext context) {
    final highestLevel =
        hazards?.hazards.fold<String>(
          'AMAN',
          (highest, item) =>
              _hazardRank(item.levelBahaya) > _hazardRank(highest)
              ? item.levelBahaya
              : highest,
        ) ??
        'AMAN';
    final color = hazardColor(highestLevel);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.13),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.circle, size: 8, color: color),
          const SizedBox(width: 6),
          Text(
            highestLevel,
            style: TextStyle(
              color: color.computeLuminance() < 0.35
                  ? const Color(0xFF8F1D1D)
                  : const Color(0xFF493800),
              fontSize: 11,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }
}

class _HazardChip extends StatelessWidget {
  const _HazardChip({required this.level, required this.label});

  final String level;
  final String label;

  @override
  Widget build(BuildContext context) {
    final color = hazardColor(level);
    final foreground = level == 'AWAS'
        ? const Color(0xFF8F1D1D)
        : level == 'SIAGA'
        ? const Color(0xFF8A3B00)
        : level == 'WASPADA'
        ? const Color(0xFF704400)
        : const Color(0xFF20533D);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: foreground,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

int _hazardRank(String level) {
  return switch (level) {
    'WASPADA' => 1,
    'SIAGA' => 2,
    'AWAS' => 3,
    _ => 0,
  };
}

class _InlineWarning extends StatelessWidget {
  const _InlineWarning({
    required this.message,
    required this.actionLabel,
    required this.onAction,
  });

  final String message;
  final String actionLabel;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.fromLTRB(12, 8, 8, 8),
      decoration: BoxDecoration(
        color: const Color(0xFFFFE6E6),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: Color(0xFFB42318)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: Color(0xFF8F1D1D),
                fontSize: 11,
                height: 1.35,
              ),
            ),
          ),
          TextButton(
            onPressed: onAction,
            child: Text(
              actionLabel,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
            ),
          ),
        ],
      ),
    );
  }
}
