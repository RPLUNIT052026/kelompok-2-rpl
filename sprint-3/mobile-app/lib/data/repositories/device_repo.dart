import 'package:dio/dio.dart';

class DeviceRepository {
  const DeviceRepository(this._dio);

  final Dio _dio;

  Future<void> registerDevice({
    required String deviceId,
    required String fcmToken,
    required String rwId,
  }) async {
    await _dio.post<void>(
      'devices/register',
      data: {'device_id': deviceId, 'fcm_token': fcmToken, 'rw_id': rwId},
    );
  }
}
