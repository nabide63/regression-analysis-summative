// Basic smoke test for the Milk Yield Predictor app.

import 'package:flutter_test/flutter_test.dart';

import 'package:milk_yield_predictor/main.dart';

void main() {
  testWidgets('App loads and shows the Predict screen', (WidgetTester tester) async {
    await tester.pumpWidget(const MilkYieldApp());

    expect(find.text('Milk Yield Predictor'), findsOneWidget);
    expect(find.text('Predict milk yield'), findsOneWidget);
  });
}
