import 'package:flutter/material.dart';

class AlertPanel extends StatelessWidget {
  const AlertPanel({super.key});

  Widget _alert(
      Color color,
      String title,
      String status,
      ) {
    return Card(
      color: color.withOpacity(.18),
      child: ListTile(
        leading: Icon(Icons.warning, color: color),
        title: Text(
          title,
          style: const TextStyle(color: Colors.white),
        ),
        subtitle: Text(
          status,
          style: const TextStyle(color: Colors.white70),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 300,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(.08),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Live Alerts",
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 22,
            ),
          ),

          const SizedBox(height: 20),

          Expanded(
            child: ListView(
              children: [
                _alert(
                  Colors.red,
                  "High Pollution",
                  "Critical",
                ),
                _alert(
                  Colors.orange,
                  "Temperature Rising",
                  "Warning",
                ),
                _alert(
                  Colors.green,
                  "All Sensors Online",
                  "Healthy",
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}