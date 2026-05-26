using Microsoft.Win32;

namespace Clipo.Services;

public static class AutoStartService
{
    private const string RunKey = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run";
    private const string AppName = "Clipo";

    public static bool IsEnabled
    {
        get
        {
            using var key = Registry.CurrentUser.OpenSubKey(RunKey);
            return key?.GetValue(AppName) is string path && path == Environment.ProcessPath;
        }
        set
        {
            using var key = Registry.CurrentUser.OpenSubKey(RunKey, writable: true);
            if (value)
                key?.SetValue(AppName, Environment.ProcessPath ?? AppName);
            else
                key?.DeleteValue(AppName, throwOnMissingValue: false);
        }
    }
}
