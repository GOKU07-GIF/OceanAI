import 'package:flutter/material.dart';

class OceanMap extends StatelessWidget {
  const OceanMap({super.key});

  Widget _sensor({
    required Alignment alignment,
    required Color color,
    required String name,
  }) {
    return Align(
      alignment: alignment,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.location_on,
            color: color,
            size: 32,
          ),
          Container(
            margin: const EdgeInsets.only(top: 4),
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: Colors.black54,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              name,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 10,
      ),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(.08),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
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
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 420,
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
            "Live Ocean Monitoring",
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 20),

          Expanded(
            child: Stack(
              children: [
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xff0D2746),
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),

                const Center(
                  child: Icon(
                    Icons.public,
                    color: Colors.white24,
                    size: 160,
                  ),
                ),

                _sensor(
                  alignment: const Alignment(-0.6, -0.4),
                  color: Colors.green,
                  name: "S-01",
                ),

                _sensor(
                  alignment: const Alignment(0.2, -0.2),
                  color: Colors.orange,
                  name: "S-02",
                ),

                _sensor(
                  alignment: const Alignment(0.5, 0.5),
                  color: Colors.red,
                  name: "S-03",
                ),

                Positioned(
                  left: 20,
                  bottom: 20,
                  right: 20,
                  child: Row(
                    mainAxisAlignment:
                        MainAxisAlignment.spaceBetween,
                    children: [
                      _statusCard(
                        "Sensors",
                        "12",
                        Colors.cyan,
                      ),
                      _statusCard(
                        "Online",
                        "10",
                        Colors.green,
                      ),
                      _statusCard(
                        "Offline",
                        "2",
                        Colors.redAccent,
                      ),
                      _statusCard(
                        "AI Status",
                        "Healthy",
                        Colors.orange,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}