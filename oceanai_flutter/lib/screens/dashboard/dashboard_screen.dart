import 'package:flutter/material.dart';

import '../../models/dashboard_stats.dart';
import '../../services/dashboard_service.dart';
import '../../widgets/backgrounds/ocean_background.dart';

import 'activity_panel.dart';
import 'ai_prediction_card.dart';
import 'alert_panel.dart';
import 'dashboard_header.dart';
import 'dashboard_sidebar.dart';
import 'ocean_map.dart';
import 'sensor_chart.dart';
import 'stat_card.dart';
import 'weather_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  DashboardStats? stats;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadDashboard();
  }

  Future<void> loadDashboard() async {
    try {
      stats = await DashboardService.getStats();
    } catch (e) {
      debugPrint(e.toString());
    }

    if (mounted) {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDesktop = MediaQuery.of(context).size.width >= 1000;

    if (loading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (stats == null) {
      return const Scaffold(
        body: Center(
          child: Text("Failed to load dashboard data"),
        ),
      );
    }

    return Scaffold(
      body: OceanBackground(
        child: Row(
          children: [
            if (isDesktop)
              const SizedBox(
                width: 270,
                child: DashboardSidebar(),
              ),

            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const DashboardHeader(),
                    const SizedBox(height: 20),

                    Expanded(
                      child: SingleChildScrollView(
                        child: Column(
                          children: [
                            GridView.count(
                              crossAxisCount: isDesktop ? 4 : 2,
                              shrinkWrap: true,
                              physics: const NeverScrollableScrollPhysics(),
                              crossAxisSpacing: 20,
                              mainAxisSpacing: 20,
                              childAspectRatio: 1.5,
                              children: [
                                StatCard(
                                  icon: Icons.water_drop,
                                  title: "Water Quality",
                                  value: stats!.waterQuality,
                                  subtitle: "Excellent",
                                  color: Colors.cyan,
                                ),
                                StatCard(
                                  icon: Icons.thermostat,
                                  title: "Temperature",
                                  value: stats!.temperature,
                                  subtitle: "Stable",
                                  color: Colors.orange,
                                ),
                                StatCard(
                                  icon: Icons.science,
                                  title: "Salinity",
                                  value: stats!.salinity,
                                  subtitle: "Normal",
                                  color: Colors.green,
                                ),
                               StatCard(
                                  icon: Icons.psychology_alt,
                                  title: "AI Risk",
                                  value: stats!.risk,
                                  subtitle: "AI Prediction",
                                  color: Colors.redAccent,
                                ),
                              ],
                            ),

                            const SizedBox(height: 25),

                            if (isDesktop)
                              const Row(
                                crossAxisAlignment:
                                    CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    flex: 2,
                                    child: OceanMap(),
                                  ),
                                  SizedBox(width: 20),
                                  Expanded(
                                    child: AIPredictionCard(),
                                  ),
                                ],
                              )
                            else
                              const Column(
                                children: [
                                  OceanMap(),
                                  SizedBox(height: 20),
                                  AIPredictionCard(),
                                ],
                              ),

                            const SizedBox(height: 25),

                            if (isDesktop)
                              const Row(
                                crossAxisAlignment:
                                    CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    flex: 2,
                                    child: SensorChart(),
                                  ),
                                  SizedBox(width: 20),
                                  Expanded(
                                    child: WeatherCard(),
                                  ),
                                ],
                              )
                            else
                              const Column(
                                children: [
                                  SensorChart(),
                                  SizedBox(height: 20),
                                  WeatherCard(),
                                ],
                              ),

                            const SizedBox(height: 25),

                            if (isDesktop)
                              const Row(
                                crossAxisAlignment:
                                    CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    child: ActivityPanel(),
                                  ),
                                  SizedBox(width: 20),
                                  Expanded(
                                    child: AlertPanel(),
                                  ),
                                ],
                              )
                            else
                              const Column(
                                children: [
                                  ActivityPanel(),
                                  SizedBox(height: 20),
                                  AlertPanel(),
                                ],
                              ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}