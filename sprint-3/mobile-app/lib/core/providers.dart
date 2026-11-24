import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:uuid/uuid.dart';

import '../data/models/hazard_response.dart';
import '../data/repositories/device_repo.dart';
import '../data/repositories/hazard_repo.dart';
import '../data/repositories/report_repo.dart';
import '../data/repositories/route_repo.dart';
import '../data/services/offline_queue_service.dart';
import 'api_client.dart';
import 'config.dart';

final apiClientProvider = Provider((ref) {
  final dio = createApiClient();
  ref.onDispose(() => dio.close(force: true));
  return dio;
});

final hazardRepositoryProvider = Provider(
  (ref) => HazardRepository(ref.watch(apiClientProvider)),
);

final routeRepositoryProvider = Provider(
  (ref) => RouteRepository(ref.watch(apiClientProvider)),
);

final deviceRepositoryProvider = Provider(
  (ref) => DeviceRepository(ref.watch(apiClientProvider)),
);

final reportRepositoryProvider = Provider<ReportRepository>(
  (ref) => ReportRepository(ref.watch(apiClientProvider)),
);

final settingsBoxProvider = Provider<Box<String>>(
  (ref) => Hive.box<String>('app_settings_box'),
);

final deviceIdProvider = FutureProvider<String>((ref) async {
  final box = ref.watch(settingsBoxProvider);
  final existingId = box.get('device_id');
  if (existingId != null && existingId.isNotEmpty) return existingId;

  const uuid = Uuid();
  final deviceId = uuid.v4();
  await box.put('device_id', deviceId);
  return deviceId;
});

final deviceRegistrationProvider = FutureProvider<void>((ref) async {
  final deviceId = await ref.watch(deviceIdProvider.future);
  await ref
      .watch(deviceRepositoryProvider)
      .registerDevice(
        deviceId: deviceId,
        fcmToken: AppConfig.fcmToken,
        rwId: AppConfig.defaultRwId,
      );
});

final hazardsProvider = FutureProvider.autoDispose<HazardResponse>(
  (ref) =>
      ref.watch(hazardRepositoryProvider).getHazards(AppConfig.defaultRwId),
);

final offlineQueueServiceProvider = Provider<OfflineQueueService>((ref) {
  final service = OfflineQueueService(
    repository: ref.watch(reportRepositoryProvider),
    box: Hive.box<String>(OfflineQueueService.boxName),
  );
  unawaited(service.start());
  ref.onDispose(() => unawaited(service.dispose()));
  return service;
});

final offlineQueueStatusProvider = StreamProvider<OfflineQueueStatus>(
  (ref) => ref.watch(offlineQueueServiceProvider).watchStatus(),
);
