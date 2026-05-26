using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Windows;
using System.Windows.Interop;
using Clipo.Helpers;
using Clipo.Models;

namespace Clipo.Services;

public class ClipboardMonitor : IDisposable
{
    private readonly StorageService _storage;
    private HwndSource? _hsource;
    private Action? _onHotkey;
    private bool _enabled = true;

    public ClipboardMonitor(StorageService storage)
    {
        _storage = storage;
    }

    public void Start(Action onHotkey)
    {
        _onHotkey = onHotkey;

        // Create a native message-only window via HwndSource (not a WPF Window)
        var parameters = new HwndSourceParameters("ClipoMessageWindow")
        {
            Width = 0,
            Height = 0,
            WindowStyle = 0,
            ExtendedWindowStyle = 0x08000000 | 0x00000080, // WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        };

        _hsource = new HwndSource(parameters);
        _hsource.AddHook(WndProc);

        var hwnd = _hsource.Handle;

        if (!NativeMethods.AddClipboardFormatListener(hwnd))
        {
            DebugWrite("AddClipboardFormatListener failed");
        }

        if (!NativeMethods.RegisterHotKey(hwnd, NativeMethods.HOTKEY_ID,
                NativeMethods.MOD_CONTROL | NativeMethods.MOD_ALT, 0x56)) // Ctrl+Alt+V
        {
            DebugWrite("RegisterHotKey (Ctrl+Alt+V) failed — hotkey may be in use by another app");
        }
    }

    private nint WndProc(nint hwnd, int msg, nint wParam, nint lParam, ref bool handled)
    {
        if (msg == NativeMethods.WM_CLIPBOARDUPDATE)
        {
            OnClipboardChanged();
        }
        else if (msg == NativeMethods.WM_HOTKEY && wParam == NativeMethods.HOTKEY_ID)
        {
            _onHotkey?.Invoke();
            handled = true;
        }
        return nint.Zero;
    }

    private void OnClipboardChanged()
    {
        if (!_enabled) return;

        try
        {
            var text = System.Windows.Clipboard.GetText(System.Windows.TextDataFormat.UnicodeText);
            if (string.IsNullOrEmpty(text)) return;

            var hash = ComputeHash(text);
            _storage.Upsert(text, ContentType.Text, hash);
        }
        catch
        {
            // Clipboard might be locked; ignore and try next time
        }
    }

    public void SetEnabled(bool enabled) => _enabled = enabled;

    private static string ComputeHash(string input)
        => Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(input)))[..16];

    private static void DebugWrite(string msg)
    {
        try
        {
            var logDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Clipo");
            Directory.CreateDirectory(logDir);
            File.AppendAllText(Path.Combine(logDir, "debug.log"), $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} {msg}\n");
        }
        catch { }
    }

    public void Dispose()
    {
        if (_hsource != null)
        {
            NativeMethods.RemoveClipboardFormatListener(_hsource.Handle);
            NativeMethods.UnregisterHotKey(_hsource.Handle, NativeMethods.HOTKEY_ID);
            _hsource.Dispose();
        }
    }
}
