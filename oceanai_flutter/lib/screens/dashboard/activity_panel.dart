import 'package:flutter/material.dart';

class ActivityPanel extends StatelessWidget {
  const ActivityPanel({super.key});

  Widget _activity(
      IconData icon,
      Color color,
      String title,
      String time,
      ) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: color.withOpacity(.2),
        child: Icon(icon, color: color),
      ),
      title: Text(
        title,
        style: const TextStyle(color: Colors.white),
      ),
      subtitle: Text(
        time,
        style: const TextStyle(color: Colors.white60),
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
            "Recent Activity",
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
                _activity(
                  Icons.water_drop,
                  Colors.cyan,
                  "Water Quality Updated",
                  "2 min ago",
                ),

                _activity(
                  Icons.psychology,
                  Colors.orange,
                  "AI Model Prediction",
                  "10 min ago",
                ),

                _activity(
                  Icons.warning,
                  Colors.red,
                  "Alert Generated",
                  "25 min ago",
                ),

                _activity(
                  Icons.cloud,
                  Colors.green,
                  "Weather Synced",
                  "1 hour ago",
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}