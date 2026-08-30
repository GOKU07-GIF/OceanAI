import 'package:flutter/material.dart';

class OceanLogo extends StatelessWidget {
  final double iconSize;
  final double titleSize;
  final double subtitleSize;

  const OceanLogo({
    super.key,
    this.iconSize = 80,
    this.titleSize = 34,
    this.subtitleSize = 16,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: iconSize + 20,
          height: iconSize + 20,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.blue.withOpacity(0.2),
                blurRadius: 15,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Icon(
            Icons.waves_rounded,
            size: iconSize,
            color: const Color(0xFF1565C0),
          ),
        ),

        const SizedBox(height: 20),

        Text(
          "OceanAI",
          style: TextStyle(
            fontSize: titleSize,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF1565C0),
            letterSpacing: 1.2,
          ),
        ),

        const SizedBox(height: 8),

        Text(
          "Smart Ocean Monitoring",
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: subtitleSize,
            color: Colors.grey.shade700,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}