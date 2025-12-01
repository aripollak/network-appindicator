import os
import signal
import gi

gi.require_version('Gtk', '3.0')

# Ubuntu/Debian now use Ayatana, while others use the older AppIndicator3.
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except (ValueError, ImportError):
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as AppIndicator
    except (ValueError, ImportError):
        print("Error: AppIndicator library not found.")
        print("Please install 'gir1.2-appindicator3-0.1' or 'libappindicator-gtk3'")
        exit(1)

from gi.repository import Gtk, GLib

APP_ID = 'network-appindicator'
INTERFACE = 'tun0'
CHECK_INTERVAL_SECONDS = 2

class VPNIndicator:
    def __init__(self):
        self.indicator = AppIndicator.Indicator.new(
            APP_ID,
            "network-vpn",
            AppIndicator.IndicatorCategory.SYSTEM_SERVICES
        )

        self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)

        self.menu = Gtk.Menu()

        item_quit = Gtk.MenuItem(label="Quit VPN Monitor")
        item_quit.connect('activate', self.quit)
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.check_vpn()
        GLib.timeout_add_seconds(CHECK_INTERVAL_SECONDS, self.check_vpn)

    def check_vpn(self):
        is_active = os.path.exists(f"/sys/class/net/{INTERFACE}")

        if is_active:
            # If VPN is on, show the icon
            if self.indicator.get_status() != AppIndicator.IndicatorStatus.ACTIVE:
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            # Show a tooltip
            self.indicator.set_icon_full("network-vpn", "VPN is active")
        else:
            # If VPN is off, hide the icon
            if self.indicator.get_status() != AppIndicator.IndicatorStatus.PASSIVE:
                self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)

        # Return True to keep the GLib timer running
        return True

    def quit(self, _source):
        Gtk.main_quit()

if __name__ == "__main__":
    # Allow Ctrl+C to kill the program from terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = VPNIndicator()

    # Start the main event loop
    Gtk.main()
