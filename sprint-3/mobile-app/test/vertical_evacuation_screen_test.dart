// Keep material.dart for compatibility with Flutter 3.x versions before 3.47.
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hyperevac_mobile/presentation/screens/vertical_evacuation_screen.dart';

void main() {
  testWidgets('renders emergency message and SAR confirmation', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: VerticalEvacuationScreen(
          message: 'Tidak ada rute aman. Lakukan evakuasi vertikal sekarang.',
          sarAlertSent: true,
          dataExpired: true,
        ),
      ),
    );

    expect(
      find.text('Tidak ada rute aman. Lakukan evakuasi vertikal sekarang.'),
      findsOneWidget,
    );
    expect(find.text('Alert SAR Terkirim'), findsOneWidget);
    expect(find.textContaining('cache terakhir'), findsOneWidget);
    expect(find.text('EVAKUASI\nVERTIKAL'), findsOneWidget);
  });
}
