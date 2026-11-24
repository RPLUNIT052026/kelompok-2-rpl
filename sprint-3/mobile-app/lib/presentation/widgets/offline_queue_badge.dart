// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';

class OfflineQueueBadge extends ConsumerWidget {
  const OfflineQueueBadge({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final queueAsync = ref.watch(offlineQueueStatusProvider);
    final status =
        queueAsync.valueOrNull ??
        ref.watch(offlineQueueServiceProvider).currentStatus;
    final hasPending = status.queuedCount > 0;
    final hasError = status.lastError != null;
    final foreground = hasError
        ? const Color(0xFF8F1D1D)
        : hasPending
        ? const Color(0xFF8A2E00)
        : const Color(0xFF20533D);
    final background = hasError
        ? const Color(0xFFFFE6E6)
        : hasPending
        ? const Color(0xFFFFE6D8)
        : const Color(0xFFE4F4EB);
    final label = hasError
        ? 'Periksa antrean'
        : status.isSyncing
        ? 'Menyinkronkan ${status.queuedCount}'
        : hasPending
        ? 'SOS antre ${status.queuedCount}'
        : status.isOnline
        ? 'SOS siap'
        : 'Offline · 0';

    return Tooltip(
      message: status.lastError ?? label,
      child: Semantics(
        label: status.lastError == null ? label : '$label. ${status.lastError}',
        child: Container(
          constraints: const BoxConstraints(minHeight: 40),
          padding: const EdgeInsets.symmetric(horizontal: 10),
          decoration: BoxDecoration(
            color: background,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                hasError
                    ? Icons.error_outline_rounded
                    : status.isSyncing
                    ? Icons.sync_rounded
                    : hasPending
                    ? Icons.cloud_upload_outlined
                    : status.isOnline
                    ? Icons.cloud_done_outlined
                    : Icons.cloud_off_outlined,
                size: 17,
                color: foreground,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  color: foreground,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
