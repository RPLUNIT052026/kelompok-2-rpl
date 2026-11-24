// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';

class StaleDataBanner extends StatelessWidget {
  const StaleDataBanner({
    super.key,
    required this.dataExpired,
    this.serviceUnavailable = false,
  });

  final bool dataExpired;
  final bool serviceUnavailable;

  @override
  Widget build(BuildContext context) {
    final warning = dataExpired || serviceUnavailable;
    final background = serviceUnavailable
        ? const Color(0xFFFFE6E6)
        : const Color(0xFFFFF3D6);
    final foreground = serviceUnavailable
        ? const Color(0xFF8F1D1D)
        : const Color(0xFF704400);
    final message = serviceUnavailable
        ? 'API tidak terjangkau. Verifikasi informasi sebelum bergerak.'
        : 'Data cache terakhir digunakan. Verifikasi kondisi melalui kanal lapangan.';

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: warning ? background : const Color(0xFFEAF2FA),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: warning
              ? foreground.withValues(alpha: 0.18)
              : const Color(0xFFD7E1EC),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            warning ? Icons.warning_amber_rounded : Icons.cloud_outlined,
            size: 19,
            color: warning ? foreground : const Color(0xFF315D85),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (warning)
                  Text(
                    message,
                    style: TextStyle(
                      color: foreground,
                      fontSize: 12,
                      height: 1.35,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                if (!warning)
                  const Text(
                    'Sumber: BMKG',
                    style: TextStyle(
                      color: Color(0xFF315D85),
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                if (warning) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Sumber: BMKG',
                    style: TextStyle(
                      color: foreground,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (dataExpired && !serviceUnavailable)
            const Padding(
              padding: EdgeInsets.only(left: 8, top: 2),
              child: Text(
                'CACHE',
                style: TextStyle(
                  color: Color(0xFF704400),
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
