import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Windows Desktop
  static const String baseUrl = "http://127.0.0.1:8000";

  static Future<http.Response> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    return await http.post(
      Uri.parse("$baseUrl$endpoint"),
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonEncode(body),
    );
  }

  static Future<http.Response> get(
    String endpoint, {
    String? token,
  }) async {
    return await http.get(
      Uri.parse("$baseUrl$endpoint"),
      headers: {
        if (token != null) "Authorization": "Bearer $token",
      },
    );
  }
}