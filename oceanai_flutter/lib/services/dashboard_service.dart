import 'dart:convert';

import '../models/dashboard_stats.dart';
import 'api_service.dart';

class DashboardService {
  static Future<DashboardStats> getStats() async {
    final response = await ApiService.get("/dashboard/stats");

    if (response.statusCode == 200) {
      return DashboardStats.fromJson(
        jsonDecode(response.body),
      );
    }

    throw Exception("Failed to load dashboard data");
  }
}