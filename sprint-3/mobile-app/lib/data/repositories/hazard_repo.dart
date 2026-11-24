import 'package:dio/dio.dart';

import '../models/hazard_response.dart';

class HazardRepository {
  const HazardRepository(this._dio);

  final Dio _dio;

  Future<HazardResponse> getHazards(String rwId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      'hazards',
      queryParameters: {'rw': rwId},
    );
    return HazardResponse.fromJson(response.data!);
  }
}
