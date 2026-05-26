using System.Windows;
using WinForms = System.Windows.Forms;
using Clipo.Services;

namespace Clipo;

public partial class App : System.Windows.Application
{
    private WinForms.NotifyIcon? _trayIcon;
    private ClipboardMonitor? _monitor;
    private StorageService? _storage;
    private PopupWindow? _popup;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        _storage = new StorageService();
        _popup = new PopupWindow(_storage);

        _monitor = new ClipboardMonitor(_storage);
        _monitor.Start(ShowPopupFromHotkey);

        SetupTrayIcon();
    }

    private void SetupTrayIcon()
    {
        var contextMenu = new WinForms.ContextMenuStrip();
        contextMenu.Items.Add(new WinForms.ToolStripMenuItem("显示 Clipo", null, (_, _) => ShowPopupFromHotkey()));
        contextMenu.Items.Add(new WinForms.ToolStripSeparator());

        WinForms.ToolStripMenuItem? autoItem = null;
        autoItem = new WinForms.ToolStripMenuItem("开机自启动", null, (_, _) =>
        {
            AutoStartService.IsEnabled = !AutoStartService.IsEnabled;
            autoItem!.Checked = AutoStartService.IsEnabled;
        })
        {
            Checked = AutoStartService.IsEnabled
        };
        contextMenu.Items.Add(autoItem);

        contextMenu.Items.Add(new WinForms.ToolStripSeparator());
        contextMenu.Items.Add(new WinForms.ToolStripMenuItem("退出", null, (_, _) => ShutdownApp()));

        _trayIcon = new WinForms.NotifyIcon
        {
            Text = "Clipo - 剪贴板管理器",
            Icon = System.Drawing.SystemIcons.Application,
            ContextMenuStrip = contextMenu,
            Visible = true
        };

        _trayIcon.DoubleClick += (_, _) => ShowPopupFromHotkey();
    }

    private void ShowPopupFromHotkey()
    {
        Dispatcher.Invoke(() => _popup?.ShowAtCursor());
    }

    private void ShutdownApp()
    {
        _trayIcon?.Dispose();
        _monitor?.Dispose();
        _storage?.Dispose();
        Current.Shutdown();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _trayIcon?.Dispose();
        _monitor?.Dispose();
        _storage?.Dispose();
        base.OnExit(e);
    }
}
