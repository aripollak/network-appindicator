import os
import signal
import gi

gi.require_version("Gtk", "3.0")

# Ubuntu/Debian now use Ayatana, while others use the older AppIndicator3.
try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except (ValueError, ImportError):
    print("Please install 'gir1.2-ayatanaappindicator3-0.1'")
    raise

from gi.repository import Gtk, GLib

APP_ID = "network-appindicator"
INTERFACE = "tun0"
CHECK_INTERVAL_SECONDS = 2
ICON_ACTIVE = "network-vpn-symbolic"
ICON_INACTIVE = "network-offline-symbolic"

class NetworkAppIndicator:
    def __init__(self):
        self.indicator = AppIndicator.Indicator.new(
            APP_ID,
            "network-vpn-acquiring-symbolic",
            AppIndicator.IndicatorCategory.SYSTEM_SERVICES
        )

        self.menu = Gtk.Menu()

        self.status_item = Gtk.MenuItem(label="Checking network interface status...")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit Network AppIndicator")
        item_quit.connect('activate', self.quit)
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.check_vpn()
        GLib.timeout_add_seconds(CHECK_INTERVAL_SECONDS, self.check_vpn)

    def check_vpn(self):
        is_active = os.path.exists(f"/sys/class/net/{INTERFACE}")

        if is_active:
            self.indicator.set_icon_full(ICON_ACTIVE, "active")
            self.status_item.set_label(f"Status: Connected ({INTERFACE})")
        else:
            self.indicator.set_icon_full(ICON_INACTIVE, "inactive")
            self.status_item.set_label(f"Status: Disconnected ({INTERFACE})")

        # Return True to keep the GLib timer running
        return True

    def quit(self, _source):
        Gtk.main_quit()

if __name__ == "__main__":
    # Allow Ctrl+C to kill the program from terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = NetworkAppIndicator()

    # Start the main event loop
    Gtk.main()
