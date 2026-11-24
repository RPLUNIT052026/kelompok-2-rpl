import 'package:dio/dio.dart';

import '../models/road_report_payload.dart';

abstract interface class ReportSubmissionRepository {
  Future<void> submitReport(RoadReportPayload payload);
}

class ReportRepository implements ReportSubmissionRepository {
  const ReportRepository(this._dio);

  final Dio _dio;

  @override
  Future<void> submitReport(RoadReportPayload payload) async {
    await _dio.post<void>('reports', data: payload.toJson());
  }
}
