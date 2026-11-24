class AppConfig {
  AppConfig._();

  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/v1',
  );
  static const defaultRwId = String.fromEnvironment(
    'DEFAULT_RW_ID',
    defaultValue: '3f0c6b1e-0000-0000-0000-000000000001',
  );
  static const fallbackLatitude = 4.4683;
  static const fallbackLongitude = 97.9683;
  static const fcmToken = String.fromEnvironment(
    'FCM_TOKEN',
    defaultValue: 'fcm-not-configured',
  );

  static String get normalizedApiBaseUrl =>
      '${apiBaseUrl.replaceFirst(RegExp(r'/+$'), '')}/';
}
