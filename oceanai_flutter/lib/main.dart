import 'package:flutter/material.dart';

import 'core/theme/app_theme.dart';
import 'screens/login/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(const OceanAIApp());
}

class OceanAIApp extends StatelessWidget {
  const OceanAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'OceanAI',
      theme: AppTheme.lightTheme,

      // For now, the app starts with the Login Screen.
      home: const LoginScreen(),
    );
  }
}