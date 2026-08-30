import 'package:flutter/material.dart';

class AIPredictionCard extends StatelessWidget {
  const AIPredictionCard({super.key});

  Widget _infoTile({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.06),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 20,
            backgroundColor: color.withOpacity(.2),
            child: Icon(
              icon,
              color: color,
              size: 20,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 380,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(.08),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withOpacity(.15),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "AI Prediction",
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 22,
            ),
          ),

          const SizedBox(height: 24),

          const Center(
            child: CircleAvatar(
              radius: 45,
              backgroundColor: Colors.blue,
              child: Icon(
                Icons.psychology_alt,
                size: 48,
                color: Colors.white,
              ),
            ),
          ),

          const SizedBox(height: 28),

          _infoTile(
            icon: Icons.check_circle,
            title: "Prediction",
            value: "Water is Safe",
            color: Colors.green,
          ),

          const SizedBox(height: 14),

          _infoTile(
            icon: Icons.analytics,
            title: "Confidence",
            value: "98.6%",
            color: Colors.cyan,
          ),

          const SizedBox(height: 14),

          _infoTile(
            icon: Icons.warning_amber,
            title: "Risk Level",
            value: "Low",
            color: Colors.orange,
          ),

          const Spacer(),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.insights),
              label: const Text("View Full Analysis"),
            ),
          ),
        ],
      ),
    );
  }
}