import 'package:flutter/material.dart';

import '../../core/constants/app_spacing.dart';
import '../../core/constants/app_strings.dart';
import '../../core/theme/app_text_styles.dart';

import '../../widgets/backgrounds/ocean_background.dart';
import '../../widgets/buttons/custom_button.dart';
import '../../widgets/cards/glass_card.dart';
import '../../widgets/inputs/custom_text_field.dart';
import '../../widgets/logo/ocean_logo.dart';

import '../../services/auth_service.dart';

import '../dashboard/dashboard_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final bool isDesktop = width >= 900;

    return Scaffold(
      body: OceanBackground(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 1200),
              child: isDesktop
                  ? const _DesktopLayout()
                  : const _MobileLayout(),
            ),
          ),
        ),
      ),
    );
  }
}

class _DesktopLayout extends StatelessWidget {
  const _DesktopLayout({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          flex: 5,
          child: Padding(
            padding: const EdgeInsets.only(right: 60),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const OceanLogo(
                  iconSize: 90,
                  titleSize: 42,
                  subtitleSize: 18,
                ),
                const SizedBox(height: 40),
                Text(
                  "AI Powered Ocean Intelligence",
                  style: AppTextStyles.heading.copyWith(
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  "Monitor marine ecosystems, analyze environmental data, and receive AI-powered insights through a modern cloud platform.",
                  style: AppTextStyles.subtitle.copyWith(
                    color: Colors.white70,
                    height: 1.7,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 50),
                Wrap(
                  spacing: 20,
                  runSpacing: 20,
                  children: const [
                    _FeatureCard(
                      icon: Icons.waves,
                      title: "Ocean Analytics",
                    ),
                    _FeatureCard(
                      icon: Icons.public,
                      title: "Live Monitoring",
                    ),
                    _FeatureCard(
                      icon: Icons.psychology,
                      title: "AI Prediction",
                    ),
                    _FeatureCard(
                      icon: Icons.shield,
                      title: "Secure Cloud",
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const Expanded(
          flex: 4,
          child: GlassCard(
            child: _LoginForm(),
          ),
        ),
      ],
    );
  }
}

class _MobileLayout extends StatelessWidget {
  const _MobileLayout({super.key});

  @override
  Widget build(BuildContext context) {
    return const GlassCard(
      child: _LoginForm(),
    );
  }
}

class _LoginForm extends StatefulWidget {
  const _LoginForm({super.key});

  @override
  State<_LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<_LoginForm> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool loading = false;

  Future<void> login() async {
    if (emailController.text.isEmpty ||
        passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Please enter email and password"),
        ),
      );
      return;
    }

    setState(() {
      loading = true;
    });

    final success = await AuthService.login(
      emailController.text.trim(),
      passwordController.text.trim(),
    );

    setState(() {
      loading = false;
    });

    if (!mounted) return;

    if (success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const DashboardScreen(),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Invalid Email or Password"),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const OceanLogo(),

        const SizedBox(height: AppSpacing.xl),

        const Text(
          AppStrings.welcome,
          textAlign: TextAlign.center,
          style: AppTextStyles.title,
        ),

        const SizedBox(height: 8),

        Text(
          "Login to continue using OceanAI",
          textAlign: TextAlign.center,
          style: AppTextStyles.subtitle.copyWith(
            height: 1.5,
          ),
        ),

        const SizedBox(height: AppSpacing.xxl),

        CustomTextField(
          controller: emailController,
          label: AppStrings.email,
          hint: "Enter your email",
          icon: Icons.email_outlined,
        ),

        const SizedBox(height: AppSpacing.lg),

        CustomTextField(
          controller: passwordController,
          label: AppStrings.password,
          hint: "Enter your password",
          icon: Icons.lock_outline,
          obscureText: true,
        ),

        const SizedBox(height: AppSpacing.xl),

       CustomButton(
  text: AppStrings.login,
  isLoading: loading,
  onPressed: () async {
    await login();
  },
),

        const SizedBox(height: AppSpacing.md),

        TextButton(
          onPressed: () {},
          child: const Text(
            AppStrings.forgotPassword,
          ),
        ),

        TextButton(
          onPressed: () {},
          child: const Text(
            AppStrings.createAccount,
          ),
        ),
      ],
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;

  const _FeatureCard({
    super.key,
    required this.icon,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 180,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.12),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: Colors.white.withOpacity(0.20),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: Colors.white.withOpacity(0.18),
            child: Icon(
              icon,
              size: 30,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}