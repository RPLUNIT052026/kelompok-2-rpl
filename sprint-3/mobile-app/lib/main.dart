// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'data/services/offline_queue_service.dart';
import 'presentation/screens/hazard_map_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  await Hive.openBox<String>('app_settings_box');
  await Hive.openBox<String>(OfflineQueueService.boxName);
  runApp(const ProviderScope(child: HyperEvacApp()));
}

class HyperEvacApp extends StatelessWidget {
  const HyperEvacApp({super.key});

  @override
  Widget build(BuildContext context) {
    const ink = Color(0xFF132238);
    const blue = Color(0xFF145DA0);

    return MaterialApp(
      title: 'HyperEvac Warga',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: blue,
          primary: blue,
          error: const Color(0xFFB42318),
          surface: Colors.white,
        ),
        scaffoldBackgroundColor: const Color(0xFFF3F6FA),
        appBarTheme: const AppBarTheme(
          foregroundColor: ink,
          elevation: 0,
          centerTitle: false,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(11)),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(11),
            borderSide: const BorderSide(color: Color(0xFFD0D8E2)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(11),
            borderSide: const BorderSide(color: blue, width: 1.5),
          ),
        ),
      ),
      home: const HazardMapScreen(),
    );
  }
}
