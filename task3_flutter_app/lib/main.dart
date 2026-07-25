import 'package:flutter/material.dart';

import 'screens/predict_screen.dart';

void main() {
  runApp(const MilkYieldApp());
}

class MilkYieldApp extends StatelessWidget {
  const MilkYieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Milk Yield Predictor',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const PredictScreen(),
    );
  }
}
