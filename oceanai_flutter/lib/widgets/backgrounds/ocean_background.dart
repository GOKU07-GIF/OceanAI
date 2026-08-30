import 'dart:math';
import 'dart:ui';

import 'package:flutter/material.dart';

class OceanBackground extends StatefulWidget {
  final Widget child;

  const OceanBackground({
    super.key,
    required this.child,
  });

  @override
  State<OceanBackground> createState() => _OceanBackgroundState();
}

class _OceanBackgroundState extends State<OceanBackground>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return Stack(
          children: [
            // Background Gradient
            Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xff0D47A1),
                    Color(0xff1565C0),
                    Color(0xff2196F3),
                    Color(0xff42A5F5),
                  ],
                ),
              ),
            ),

            // Animated bubbles
            ...List.generate(
              15,
              (index) {
                final size = 40.0 + (index * 8);

                final dx = (index * 90) % 1400;

                final dy =
                    (index * 120 + (_controller.value * 500)) % 900;

                return Positioned(
                  left: dx.toDouble(),
                  top: 900 - dy,
                  child: Opacity(
                    opacity: 0.08,
                    child: Container(
                      width: size,
                      height: size,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                );
              },
            ),

            // Top Glow
            Positioned(
              top: -150,
              right: -120,
              child: _glowCircle(
                350,
                Colors.white.withOpacity(.12),
              ),
            ),

            // Bottom Left Glow
            Positioned(
              bottom: -180,
              left: -120,
              child: _glowCircle(
                380,
                Colors.cyan.withOpacity(.15),
              ),
            ),

            // Center Glow
            Positioned(
              top: 250,
              left: 300 + sin(_controller.value * pi * 2) * 25,
              child: _glowCircle(
                220,
                Colors.lightBlueAccent.withOpacity(.08),
              ),
            ),

            // Glass Overlay
            BackdropFilter(
              filter: ImageFilter.blur(
                sigmaX: 3,
                sigmaY: 3,
              ),
              child: Container(
                color: Colors.transparent,
              ),
            ),

            SafeArea(
              child: widget.child,
            ),
          ],
        );
      },
    );
  }

  Widget _glowCircle(double size, Color color) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    );
  }
}