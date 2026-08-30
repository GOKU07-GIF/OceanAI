import 'package:flutter/material.dart';

class DashboardSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int>? onItemSelected;

  const DashboardSidebar({
    super.key,
    this.selectedIndex = 0,
    this.onItemSelected,
  });

  static const List<_SidebarItem> _menuItems = [
    _SidebarItem(Icons.dashboard_rounded, "Dashboard"),
    _SidebarItem(Icons.map_rounded, "Ocean Map"),
    _SidebarItem(Icons.sensors_rounded, "Sensors"),
    _SidebarItem(Icons.psychology_alt_rounded, "AI Prediction"),
    _SidebarItem(Icons.analytics_rounded, "Analytics"),
    _SidebarItem(Icons.warning_amber_rounded, "Alerts"),
    _SidebarItem(Icons.description_rounded, "Reports"),
    _SidebarItem(Icons.settings_rounded, "Settings"),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 270,
      margin: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        color: Colors.white.withOpacity(0.08),
        border: Border.all(
          color: Colors.white.withOpacity(0.15),
        ),
      ),
      child: Column(
        children: [
          const SizedBox(height: 28),

          const CircleAvatar(
            radius: 38,
            backgroundColor: Colors.white,
            child: Icon(
              Icons.waves,
              size: 42,
              color: Color(0xff0A84FF),
            ),
          ),

          const SizedBox(height: 18),

          const Text(
            "OceanAI",
            style: TextStyle(
              fontSize: 26,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),

          const SizedBox(height: 4),

          const Text(
            "Marine Intelligence",
            style: TextStyle(
              color: Colors.white60,
              fontSize: 13,
            ),
          ),

          const SizedBox(height: 34),

          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: _menuItems.length,
              itemBuilder: (context, index) {
                final item = _menuItems[index];
                final selected = index == selectedIndex;

                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => onItemSelected?.call(index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 250),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 14,
                      ),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        color: selected
                            ? Colors.blue.withOpacity(0.22)
                            : Colors.transparent,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            item.icon,
                            color: selected
                                ? Colors.white
                                : Colors.white70,
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Text(
                              item.title,
                              style: TextStyle(
                                color: selected
                                    ? Colors.white
                                    : Colors.white70,
                                fontWeight: selected
                                    ? FontWeight.bold
                                    : FontWeight.w500,
                                fontSize: 15,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          const Divider(
            color: Colors.white24,
            indent: 18,
            endIndent: 18,
          ),

          ListTile(
            leading: const Icon(
              Icons.logout_rounded,
              color: Colors.redAccent,
            ),
            title: const Text(
              "Logout",
              style: TextStyle(
                color: Colors.redAccent,
                fontWeight: FontWeight.w600,
              ),
            ),
            onTap: () {},
          ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _SidebarItem {
  final IconData icon;
  final String title;

  const _SidebarItem(this.icon, this.title);
}