import 'package:dio/dio.dart';

import '../models/evacuation_response.dart';

class RouteRepository {
  const RouteRepository(this._dio);

  final Dio _dio;

  Future<EvacuationResponse> getEvacuationRoutes({
    required double latitude,
    required double longitude,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      'routes/evacuation',
      queryParameters: {'lat': latitude, 'lng': longitude},
    );
    return EvacuationResponse.fromJson(response.data!);
  }
}
