import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class SensorChart extends StatelessWidget {
  const SensorChart({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 380,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withOpacity(0.15),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Sensor Analytics",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Chip(
                label: Text("Last 24 Hours"),
              ),
            ],
          ),

          const SizedBox(height: 30),

          Expanded(
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 10,
                ),

                borderData: FlBorderData(show: false),

                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 35,
                    ),
                  ),
                  rightTitles: const AxisTitles(),
                  topTitles: const AxisTitles(),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                    ),
                  ),
                ),

                minX: 0,
                maxX: 6,
                minY: 0,
                maxY: 100,

                lineBarsData: [
                  LineChartBarData(
                    isCurved: true,
                    color: Colors.cyan,
                    barWidth: 4,
                    dotData: const FlDotData(show: false),
                    spots: const [
                      FlSpot(0, 35),
                      FlSpot(1, 48),
                      FlSpot(2, 42),
                      FlSpot(3, 65),
                      FlSpot(4, 58),
                      FlSpot(5, 72),
                      FlSpot(6, 82),
                    ],
                  ),

                  LineChartBarData(
                    isCurved: true,
                    color: Colors.orange,
                    barWidth: 4,
                    dotData: const FlDotData(show: false),
                    spots: const [
                      FlSpot(0, 20),
                      FlSpot(1, 28),
                      FlSpot(2, 40),
                      FlSpot(3, 44),
                      FlSpot(4, 48),
                      FlSpot(5, 55),
                      FlSpot(6, 62),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 20),

          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _Legend(
                color: Colors.cyan,
                text: "Water Quality",
              ),
              _Legend(
                color: Colors.orange,
                text: "Temperature",
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  final Color color;
  final String text;

  const _Legend({
    required this.color,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          height: 12,
          width: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          text,
          style: const TextStyle(
            color: Colors.white70,
          ),
        ),
      ],
    );
  }
}