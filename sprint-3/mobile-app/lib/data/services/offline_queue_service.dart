import 'dart:async';
import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:uuid/uuid.dart';

import '../../core/api_client.dart';
import '../models/road_report_payload.dart';
import '../repositories/report_repo.dart';

typedef ConnectivityStream = Stream<List<ConnectivityResult>> Function();
typedef ConnectivityCheck = Future<List<ConnectivityResult>> Function();
typedef QueueIdGenerator = String Function();

class OfflineQueueStatus {
  const OfflineQueueStatus({
    required this.isOnline,
    required this.isSyncing,
    required this.queuedCount,
    required this.lastError,
  });

  final bool isOnline;
  final bool isSyncing;
  final int queuedCount;
  final String? lastError;
}

class QueueSubmitResult {
  const QueueSubmitResult({required this.queued});

  final bool queued;
}

class OfflineQueueService {
  OfflineQueueService({
    required ReportSubmissionRepository repository,
    required Box<String> box,
    ConnectivityStream? watchConnectivity,
    ConnectivityCheck? checkConnectivity,
    QueueIdGenerator? idGenerator,
  }) : _repository = repository,
       _box = box,
       _watchConnectivity =
           watchConnectivity ?? (() => Connectivity().onConnectivityChanged),
       _checkConnectivity =
           checkConnectivity ?? (() => Connectivity().checkConnectivity()),
       _idGenerator = idGenerator ?? const Uuid().v4,
       _status = OfflineQueueStatus(
         isOnline: false,
         isSyncing: false,
         queuedCount: box.length,
         lastError: null,
       );

  static const boxName = 'offline_reports_box';

  final ReportSubmissionRepository _repository;
  final Box<String> _box;
  final ConnectivityStream _watchConnectivity;
  final ConnectivityCheck _checkConnectivity;
  final QueueIdGenerator _idGenerator;
  final StreamController<OfflineQueueStatus> _statusController =
      StreamController<OfflineQueueStatus>.broadcast();

  late OfflineQueueStatus _status;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;
  bool _started = false;

  OfflineQueueStatus get currentStatus => _status;

  Stream<OfflineQueueStatus> watchStatus() async* {
    yield _status;
    yield* _statusController.stream;
  }

  Future<void> start() async {
    if (_started) return;
    _started = true;
    _connectivitySubscription = _watchConnectivity().listen(
      (results) => unawaited(_handleConnectivity(results)),
      onError: (Object error) {
        _publish(lastError: 'Status jaringan tidak dapat dipantau: $error');
      },
    );

    try {
      await _handleConnectivity(await _checkConnectivity());
    } catch (error) {
      _publish(lastError: 'Status jaringan tidak dapat diperiksa: $error');
    }
  }

  Future<QueueSubmitResult> submitReport(RoadReportPayload payload) async {
    if (!_status.isOnline) return _enqueue(payload);

    try {
      await _repository.submitReport(payload);
      return const QueueSubmitResult(queued: false);
    } on DioException catch (error) {
      if (!isNetworkFailure(error)) rethrow;
      _publish(isOnline: false, lastError: apiErrorMessage(error));
      return _enqueue(payload);
    }
  }

  Future<int> flush() async {
    if (!_status.isOnline || _status.isSyncing || _box.isEmpty) return 0;
    _publish(isSyncing: true, clearError: true);
    var sentCount = 0;

    for (final key in _box.keys.toList()) {
      final serialized = _box.get(key);
      if (serialized == null) {
        _publish(
          lastError: 'Laporan antrean $key tidak memiliki data tersimpan.',
        );
        break;
      }

      try {
        final payload = RoadReportPayload.fromJson(
          jsonDecode(serialized) as Map<String, dynamic>,
        );
        await _repository.submitReport(payload);
        await _box.delete(key);
        sentCount++;
        _publish(clearError: true);
      } on DioException catch (error) {
        if (isNetworkFailure(error)) {
          _publish(
            isOnline: false,
            lastError: 'Sinkronisasi tertunda: ${apiErrorMessage(error)}',
          );
        } else {
          _publish(
            lastError:
                'Laporan antrean gagal diterima API: ${apiErrorMessage(error)}',
          );
        }
        break;
      } on FormatException catch (error) {
        _publish(
          lastError: 'Data laporan antrean tidak valid: ${error.message}',
        );
        break;
      } on TypeError catch (error) {
        _publish(lastError: 'Format laporan antrean tidak sesuai: $error');
        break;
      }
    }

    _publish(isSyncing: false);
    return sentCount;
  }

  Future<void> dispose() async {
    await _connectivitySubscription?.cancel();
    await _statusController.close();
  }

  Future<void> _handleConnectivity(List<ConnectivityResult> results) async {
    final isOnline = results.any((result) => result != ConnectivityResult.none);
    _publish(isOnline: isOnline, clearError: isOnline);
    if (isOnline) await flush();
  }

  Future<QueueSubmitResult> _enqueue(RoadReportPayload payload) async {
    final queueId = _idGenerator();
    await _box.put(queueId, jsonEncode(payload.toJson()));
    _publish(lastError: null, clearError: true);
    return const QueueSubmitResult(queued: true);
  }

  void _publish({
    bool? isOnline,
    bool? isSyncing,
    String? lastError,
    bool clearError = false,
  }) {
    _status = OfflineQueueStatus(
      isOnline: isOnline ?? _status.isOnline,
      isSyncing: isSyncing ?? _status.isSyncing,
      queuedCount: _box.length,
      lastError: clearError ? null : lastError ?? _status.lastError,
    );
    if (!_statusController.isClosed) _statusController.add(_status);
  }
}
