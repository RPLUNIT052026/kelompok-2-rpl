import 'dart:async';
import 'dart:io';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:hyperevac_mobile/data/models/road_report_payload.dart';
import 'package:hyperevac_mobile/data/repositories/report_repo.dart';
import 'package:hyperevac_mobile/data/services/offline_queue_service.dart';

void main() {
  late Directory tempDirectory;
  late Box<String> box;
  late StreamController<List<ConnectivityResult>> connectivity;
  late _FakeReportRepository repository;
  late OfflineQueueService service;

  setUp(() async {
    tempDirectory = await Directory.systemTemp.createTemp('hyperevac_queue_');
    Hive.init(tempDirectory.path);
    box = await Hive.openBox<String>(OfflineQueueService.boxName);
    connectivity = StreamController<List<ConnectivityResult>>.broadcast();
    repository = _FakeReportRepository();
    service = OfflineQueueService(
      repository: repository,
      box: box,
      watchConnectivity: () => connectivity.stream,
      checkConnectivity: () async => [ConnectivityResult.none],
      idGenerator: () => 'queued-report-1',
    );
  });

  tearDown(() async {
    await service.dispose();
    await connectivity.close();
    await Hive.close();
    await tempDirectory.delete(recursive: true);
  });

  test(
    'persists offline report and auto-syncs when connectivity returns',
    () async {
      await service.start();
      final payload = RoadReportPayload(
        deviceId: 'device-1',
        segmentId: 'b7a6c5d4-0000-0000-0000-000000000030',
        type: 'tertutup',
        latitude: 4.4683,
        longitude: 97.9683,
        note: 'Genangan menutup jalan',
        createdAt: DateTime.utc(2026, 9, 29, 8),
      );

      final result = await service.submitReport(payload);
      expect(result.queued, isTrue);
      expect(box.length, 1);
      expect(box.get('queued-report-1'), contains('"device_id":"device-1"'));
      expect(service.currentStatus.queuedCount, 1);

      connectivity.add([ConnectivityResult.wifi]);
      await repository.firstSubmission.timeout(const Duration(seconds: 2));
      await Future<void>.delayed(const Duration(milliseconds: 50));

      expect(repository.submissions, hasLength(1));
      expect(repository.submissions.single.segmentId, payload.segmentId);
      expect(repository.submissions.single.createdAt, payload.createdAt);
      expect(box.length, 0);
      expect(service.currentStatus.queuedCount, 0);
      expect(service.currentStatus.isOnline, isTrue);
    },
  );
}

class _FakeReportRepository implements ReportSubmissionRepository {
  final List<RoadReportPayload> submissions = [];
  final Completer<void> _firstSubmission = Completer<void>();

  Future<void> get firstSubmission => _firstSubmission.future;

  @override
  Future<void> submitReport(RoadReportPayload payload) async {
    submissions.add(payload);
    if (!_firstSubmission.isCompleted) _firstSubmission.complete();
  }
}
