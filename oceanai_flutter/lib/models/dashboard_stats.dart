class DashboardStats {
  final String waterQuality;
  final String temperature;
  final String salinity;
  final String risk;

  DashboardStats({
    required this.waterQuality,
    required this.temperature,
    required this.salinity,
    required this.risk,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      waterQuality: json["water_quality"],
      temperature: json["temperature"],
      salinity: json["salinity"],
      risk: json["risk"],
    );
  }
}