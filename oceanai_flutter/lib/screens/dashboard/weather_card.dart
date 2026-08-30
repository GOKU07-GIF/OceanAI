import 'package:flutter/material.dart';

class WeatherCard extends StatelessWidget {
  const WeatherCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 350,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.12),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withOpacity(0.20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          const Icon(
            Icons.cloud,
            size: 70,
            color: Colors.white,
          ),

          const SizedBox(height: 15),

          const Text(
            "Mumbai",
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 6),

          const Text(
            "Partly Cloudy",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 16,
            ),
          ),

          const SizedBox(height: 25),

          const Text(
            "29°C",
            style: TextStyle(
              color: Colors.white,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 30),

          const Divider(color: Colors.white24),

          const SizedBox(height: 15),

          const _WeatherInfoRow(
            icon: Icons.water_drop,
            title: "Humidity",
            value: "78%",
          ),

          const SizedBox(height: 15),

          const _WeatherInfoRow(
            icon: Icons.air,
            title: "Wind Speed",
            value: "14 km/h",
          ),

          const SizedBox(height: 15),

          const _WeatherInfoRow(
            icon: Icons.waves,
            title: "Wave Height",
            value: "1.8 m",
          ),

          const SizedBox(height: 15),

          const _WeatherInfoRow(
            icon: Icons.visibility,
            title: "Visibility",
            value: "8 km",
          ),
        ],
      ),
    );
  }
}

class _WeatherInfoRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;

  const _WeatherInfoRow({
    required this.icon,
    required this.title,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          icon,
          color: Colors.white,
          size: 22,
        ),

        const SizedBox(width: 12),

        Expanded(
          child: Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 15,
            ),
          ),
        ),

        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 15,
          ),
        ),
      ],
    );
  }
}