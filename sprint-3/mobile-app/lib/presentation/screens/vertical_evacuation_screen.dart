// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';

import '../widgets/stale_data_banner.dart';

class VerticalEvacuationScreen extends StatelessWidget {
  const VerticalEvacuationScreen({
    super.key,
    required this.message,
    required this.sarAlertSent,
    this.dataExpired = false,
  });

  final String message;
  final bool sarAlertSent;
  final bool dataExpired;

  @override
  Widget build(BuildContext context) {
    final displayedMessage = message.trim().isEmpty
        ? 'Tidak ada rute aman. Lakukan evakuasi vertikal ke lokasi kokoh terdekat.'
        : message.trim();

    return Scaffold(
      backgroundColor: const Color(0xFF8F1D1D),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 10, 18, 6),
              child: Row(
                children: [
                  IconButton(
                    tooltip: 'Kembali ke peta bahaya',
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.arrow_back_rounded),
                    color: Colors.white,
                  ),
                  const Expanded(
                    child: Text(
                      'INSTRUKSI DARURAT',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ),
                  const SizedBox(width: 48),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(22, 14, 22, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 13,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFD8D6),
                        borderRadius: BorderRadius.circular(30),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.crisis_alert_rounded,
                            color: Color(0xFF8F1D1D),
                            size: 18,
                          ),
                          SizedBox(width: 7),
                          Text(
                            'TIDAK ADA RUTE DARAT AMAN',
                            style: TextStyle(
                              color: Color(0xFF8F1D1D),
                              fontSize: 11,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.45,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 22),
                    const Icon(
                      Icons.stairs_rounded,
                      color: Colors.white,
                      size: 68,
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'EVAKUASI\nVERTIKAL',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 33,
                        height: 1.02,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 18),
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'PESAN DARURAT',
                            style: TextStyle(
                              color: Color(0xFF8F1D1D),
                              fontSize: 10,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.8,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            displayedMessage,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              color: Color(0xFF182230),
                              fontSize: 18,
                              height: 1.4,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 15),
                          Container(
                            constraints: const BoxConstraints(minHeight: 50),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 9,
                            ),
                            decoration: BoxDecoration(
                              color: sarAlertSent
                                  ? const Color(0xFFE4F4EB)
                                  : const Color(0xFFFFF3D6),
                              borderRadius: BorderRadius.circular(11),
                              border: Border.all(
                                color: sarAlertSent
                                    ? const Color(0xFF9BC9AD)
                                    : const Color(0xFFE6C777),
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  sarAlertSent
                                      ? Icons.notifications_active_rounded
                                      : Icons.notifications_paused_outlined,
                                  color: sarAlertSent
                                      ? const Color(0xFF20533D)
                                      : const Color(0xFF704400),
                                ),
                                const SizedBox(width: 8),
                                Flexible(
                                  child: Text(
                                    sarAlertSent
                                        ? 'Alert SAR Terkirim'
                                        : 'Alert SAR belum dikonfirmasi',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      color: sarAlertSent
                                          ? const Color(0xFF20533D)
                                          : const Color(0xFF704400),
                                      fontSize: 13,
                                      fontWeight: FontWeight.w900,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 17),
                    const Text(
                      'LAKUKAN SEKARANG',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 9),
                    const _EmergencyInstruction(
                      number: '1',
                      text:
                          'Menuju lantai atau tempat tertinggi di bangunan yang kokoh.',
                    ),
                    const _EmergencyInstruction(
                      number: '2',
                      text:
                          'Jangan berjalan menerobos arus dan jangan gunakan lift.',
                    ),
                    const _EmergencyInstruction(
                      number: '3',
                      text:
                          'Bawa ponsel, obat penting, dan beri tahu petugas lokasi Anda.',
                    ),
                    const SizedBox(height: 16),
                    StaleDataBanner(dataExpired: dataExpired),
                    const SizedBox(height: 2),
                    FilledButton.icon(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.map_outlined),
                      label: const Text('Kembali ke Peta Bahaya'),
                      style: FilledButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF8F1D1D),
                        minimumSize: const Size.fromHeight(54),
                        textStyle: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w900,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(13),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Ikuti arahan petugas penyelamat di lokasi.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Color(0xFFFFD8D6), fontSize: 11),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmergencyInstruction extends StatelessWidget {
  const _EmergencyInstruction({required this.number, required this.text});

  final String number;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 7),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(11),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 23,
            height: 23,
            alignment: Alignment.center,
            decoration: const BoxDecoration(
              color: Color(0xFFB42318),
              shape: BoxShape.circle,
            ),
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: Color(0xFF182230),
                fontSize: 12,
                height: 1.35,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
