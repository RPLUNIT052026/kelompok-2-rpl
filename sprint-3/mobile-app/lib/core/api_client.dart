import 'package:dio/dio.dart';

import 'config.dart';

Dio createApiClient({String? baseUrl}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl ?? AppConfig.normalizedApiBaseUrl,
      connectTimeout: const Duration(seconds: 8),
      receiveTimeout: const Duration(seconds: 12),
      sendTimeout: const Duration(seconds: 8),
      headers: const {'Accept': 'application/json'},
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onError: (error, handler) {
        final message = apiErrorMessage(error);
        error = error.copyWith(message: message, error: message);
        handler.next(error);
      },
    ),
  );

  return dio;
}

String apiErrorMessage(Object error) {
  if (error is! DioException) return error.toString();

  final responseData = error.response?.data;
  if (responseData is Map<String, dynamic>) {
    final apiError = responseData['error'];
    if (apiError is Map<String, dynamic> && apiError['message'] is String) {
      return apiError['message'] as String;
    }

    final detail = responseData['detail'];
    if (detail is String) return detail;
    if (detail is Map<String, dynamic> && detail['message'] is String) {
      return detail['message'] as String;
    }
  }

  if (error.type == DioExceptionType.connectionTimeout ||
      error.type == DioExceptionType.sendTimeout ||
      error.type == DioExceptionType.receiveTimeout) {
    return 'Koneksi API melewati batas waktu. Laporan akan tetap dapat diantrekan.';
  }
  if (error.type == DioExceptionType.connectionError) {
    return 'Tidak dapat terhubung ke API. Periksa jaringan dan alamat server.';
  }
  return error.message ?? 'Permintaan API gagal.';
}

bool isNetworkFailure(Object error) {
  if (error is! DioException) return false;
  return error.type == DioExceptionType.connectionError ||
      error.type == DioExceptionType.connectionTimeout ||
      error.type == DioExceptionType.sendTimeout ||
      error.type == DioExceptionType.receiveTimeout;
}
