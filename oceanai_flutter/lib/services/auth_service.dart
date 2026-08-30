import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';

class AuthService {
  static Future<bool> login(
    String email,
    String password,
  ) async {
    final response = await ApiService.post(
      "/auth/login",
      {
        "email": email,
        "password": password,
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final prefs = await SharedPreferences.getInstance();

      await prefs.setString(
        "token",
        data["access_token"],
      );

      return true;
    }

    return false;
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();

    return prefs.getString("token");
  }

  static Future logout() async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.clear();
  }
}