// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../data/models/evacuation_response.dart';
import '../../data/models/road_report_payload.dart';

class SosReportModal extends ConsumerStatefulWidget {
  const SosReportModal({
    super.key,
    required this.deviceId,
    required this.position,
    required this.segments,
  });

  final String deviceId;
  final LatLng position;
  final List<RouteSegment> segments;

  @override
  ConsumerState<SosReportModal> createState() => _SosReportModalState();
}

class _SosReportModalState extends ConsumerState<SosReportModal> {
  final _formKey = GlobalKey<FormState>();
  final _noteController = TextEditingController();
  final _manualSegmentController = TextEditingController();
  String _type = 'tertutup';
  String? _selectedSegmentId;
  bool _sending = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    if (widget.segments.isNotEmpty) {
      _selectedSegmentId = widget.segments.first.segmentId;
    }
  }

  @override
  void dispose() {
    _noteController.dispose();
    _manualSegmentController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final segmentId = widget.segments.isEmpty
        ? _manualSegmentController.text.trim()
        : _selectedSegmentId;
    if (segmentId == null || segmentId.isEmpty) return;

    setState(() {
      _sending = true;
      _errorMessage = null;
    });
    final messenger = ScaffoldMessenger.of(context);
    try {
      final result = await ref
          .read(offlineQueueServiceProvider)
          .submitReport(
            RoadReportPayload(
              deviceId: widget.deviceId,
              segmentId: segmentId,
              type: _type,
              latitude: widget.position.latitude,
              longitude: widget.position.longitude,
              note: _noteController.text.trim(),
              createdAt: DateTime.now().toUtc(),
            ),
          );
      if (!mounted) return;
      Navigator.of(context).pop(true);
      messenger.showSnackBar(
        SnackBar(
          behavior: SnackBarBehavior.floating,
          backgroundColor: result.queued
              ? const Color(0xFF704400)
              : const Color(0xFF20533D),
          content: Text(
            result.queued
                ? 'SOS disimpan. Laporan akan dikirim saat koneksi pulih.'
                : 'Laporan SOS berhasil dikirim ke operator.',
          ),
        ),
      );
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _sending = false;
        _errorMessage = apiErrorMessage(error);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final segments = widget.segments
        .where((segment) => segment.segmentId.isNotEmpty)
        .toList(growable: false);

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 12,
          bottom: MediaQuery.viewInsetsOf(context).bottom + 20,
        ),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 42,
                    height: 4,
                    decoration: BoxDecoration(
                      color: const Color(0xFFCBD5E1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                const Row(
                  children: [
                    Icon(Icons.sos_rounded, color: Color(0xFFB42318), size: 26),
                    SizedBox(width: 9),
                    Expanded(
                      child: Text(
                        'Laporan SOS Lapangan',
                        style: TextStyle(
                          color: Color(0xFF182230),
                          fontSize: 19,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 7),
                Text(
                  'Pilih kondisi ruas yang Anda lihat. Waktu dan koordinat dicatat saat tombol kirim ditekan.',
                  style: TextStyle(
                    color: Colors.blueGrey.shade700,
                    fontSize: 13,
                    height: 1.45,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'KONDISI RUAS',
                  style: TextStyle(
                    color: Color(0xFF475467),
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.6,
                  ),
                ),
                const SizedBox(height: 8),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(
                      value: 'tertutup',
                      label: Text('Tertutup'),
                      icon: Icon(Icons.block_rounded),
                    ),
                    ButtonSegment(
                      value: 'aman',
                      label: Text('Aman'),
                      icon: Icon(Icons.check_circle_outline_rounded),
                    ),
                  ],
                  selected: {_type},
                  onSelectionChanged: _sending
                      ? null
                      : (selection) => setState(() => _type = selection.first),
                  showSelectedIcon: false,
                ),
                const SizedBox(height: 16),
                if (segments.isNotEmpty) ...[
                  const Text(
                    'RUAS YANG DILAPORKAN',
                    style: TextStyle(
                      color: Color(0xFF475467),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.6,
                    ),
                  ),
                  const SizedBox(height: 7),
                  DropdownButtonFormField<String>(
                    initialValue:
                        segments.any(
                          (item) => item.segmentId == _selectedSegmentId,
                        )
                        ? _selectedSegmentId
                        : segments.first.segmentId,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                    ),
                    items: segments.map((segment) {
                      return DropdownMenuItem(
                        value: segment.segmentId,
                        child: Text(
                          '${segment.segmentId.substring(0, 8).toUpperCase()} · ${segment.status}',
                          overflow: TextOverflow.ellipsis,
                        ),
                      );
                    }).toList(),
                    onChanged: _sending
                        ? null
                        : (value) => setState(() => _selectedSegmentId = value),
                  ),
                ] else ...[
                  const Text(
                    'ID RUAS',
                    style: TextStyle(
                      color: Color(0xFF475467),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.6,
                    ),
                  ),
                  const SizedBox(height: 7),
                  TextFormField(
                    controller: _manualSegmentController,
                    enabled: !_sending,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'UUID ruas dari papan/laporan petugas',
                      prefixIcon: Icon(Icons.route_outlined),
                    ),
                    validator: (value) {
                      final trimmed = value?.trim() ?? '';
                      if (!RegExp(
                        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
                      ).hasMatch(trimmed)) {
                        return 'Masukkan UUID ruas yang valid.';
                      }
                      return null;
                    },
                  ),
                ],
                const SizedBox(height: 15),
                TextFormField(
                  controller: _noteController,
                  enabled: !_sending,
                  maxLength: 1000,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Catatan kondisi',
                    hintText:
                        'Contoh: genangan setinggi betis di dekat jembatan',
                    alignLabelWithHint: true,
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Lokasi GPS: ${widget.position.latitude.toStringAsFixed(5)}, ${widget.position.longitude.toStringAsFixed(5)}',
                  style: const TextStyle(
                    color: Color(0xFF475467),
                    fontSize: 11,
                    fontFamily: 'monospace',
                  ),
                ),
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(11),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFE6E6),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(
                        color: Color(0xFF8F1D1D),
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 14),
                FilledButton.icon(
                  onPressed: _sending ? null : _submit,
                  icon: _sending
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.send_rounded),
                  label: Text(
                    _sending ? 'Mengirim laporan…' : 'Kirim Laporan SOS',
                  ),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(56),
                    backgroundColor: const Color(0xFFB42318),
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Laporan "aman" tidak membuka ruas secara otomatis.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF667085), fontSize: 11),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
