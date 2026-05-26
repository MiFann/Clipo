using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using Clipo.Helpers;
using Clipo.Models;
using Clipo.Services;

namespace Clipo;

public partial class PopupWindow : Window
{
    private readonly StorageService _storage;
    private nint _previousForeground;

    public PopupWindow(StorageService storage)
    {
        InitializeComponent();
        _storage = storage;
    }

    public void ShowAtCursor()
    {
        if (IsVisible)
        {
            HideWindow();
            return;
        }

        _previousForeground = NativeMethods.GetForegroundWindow();

        NativeMethods.GetCursorPos(out var pt);

        var mi = new NativeMethods.MONITORINFO();
        mi.cbSize = Marshal.SizeOf(mi);
        NativeMethods.GetMonitorInfo(NativeMethods.MonitorFromPoint(pt, NativeMethods.MONITOR_DEFAULTTONEAREST), ref mi);

        var workArea = mi.rcWork;
        double left = pt.X - 200;
        double top = pt.Y + 20;

        if (left < workArea.Left) left = workArea.Left + 8;
        if (left + Width > workArea.Right) left = workArea.Right - Width - 8;
        if (top + Height > workArea.Bottom) top = pt.Y - Height - 10;
        if (top < workArea.Top) top = workArea.Top + 8;

        Left = left;
        Top = top;

        RefreshList();
        Show();
        Activate();
        SearchBox.Focus();
    }

    public void HideWindow()
    {
        Hide();
        SearchBox.Clear();
    }

    private void RefreshList(string? query = null)
    {
        var items = _storage.Search(query);
        HistoryList.ItemsSource = items;

        if (items.Count > 0)
            HistoryList.SelectedIndex = 0;
    }

    // --- Drag bar ---

    private void DragBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        DragMove();
    }

    private void CloseButton_Click(object sender, MouseButtonEventArgs e)
    {
        HideWindow();
        e.Handled = true;
    }

    // --- Search ---

    private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
        => RefreshList(SearchBox.Text);

    private void ClearSearch_Click(object sender, MouseButtonEventArgs e)
    {
        SearchBox.Clear();
        SearchBox.Focus();
    }

    private void SearchBox_PreviewKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
    {
        switch (e.Key)
        {
            case Key.Down:
                if (HistoryList.SelectedIndex < HistoryList.Items.Count - 1)
                    HistoryList.SelectedIndex++;
                HistoryList.ScrollIntoView(HistoryList.SelectedItem);
                e.Handled = true;
                break;
            case Key.Up:
                if (HistoryList.SelectedIndex > 0)
                    HistoryList.SelectedIndex--;
                HistoryList.ScrollIntoView(HistoryList.SelectedItem);
                e.Handled = true;
                break;
            case Key.Enter:
                PasteSelected();
                e.Handled = true;
                break;
            case Key.Escape:
                HideWindow();
                e.Handled = true;
                break;
        }
    }

    // --- Single-click paste ---

    private void HistoryList_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        // Only trigger paste when clicking on an actual item, not on empty space
        var item = GetItemFromEventSource(e.OriginalSource);
        if (item != null)
        {
            HistoryList.SelectedItem = item;
            PasteSelected();
            e.Handled = true;
        }
    }

    private static ClipboardItem? GetItemFromEventSource(object source)
    {
        if (source is FrameworkElement fe && fe.DataContext is ClipboardItem item)
            return item;
        if (source is System.Windows.Media.Visual v)
        {
            var parent = System.Windows.Media.VisualTreeHelper.GetParent(v);
            while (parent != null)
            {
                if (parent is FrameworkElement pfe && pfe.DataContext is ClipboardItem pitem)
                    return pitem;
                parent = System.Windows.Media.VisualTreeHelper.GetParent(parent);
            }
        }
        return null;
    }

    private async void PasteSelected()
    {
        if (HistoryList.SelectedItem is not ClipboardItem item) return;

        HideWindow();

        try
        {
            System.Windows.Clipboard.SetText(item.Content);
        }
        catch
        {
            return;
        }

        await Task.Delay(50);

        if (_previousForeground != nint.Zero)
            NativeMethods.SetForegroundWindow(_previousForeground);

        await Task.Delay(30);

        NativeMethods.SimulateCtrlV();
    }

    private void Window_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
    {
        if (e.Key == Key.Escape)
        {
            HideWindow();
            e.Handled = true;
        }
    }


    // --- Context menu handlers ---

    private void MenuPaste_Click(object sender, RoutedEventArgs e)
    {
        if (HistoryList.SelectedItem is not ClipboardItem) return;
        PasteSelected();
    }

    private void MenuCopy_Click(object sender, RoutedEventArgs e)
    {
        if (HistoryList.SelectedItem is not ClipboardItem item) return;
        try { System.Windows.Clipboard.SetText(item.Content); } catch { }
    }

    private void MenuPin_Click(object sender, RoutedEventArgs e)
    {
        if (HistoryList.SelectedItem is not ClipboardItem item) return;

        var newPin = !item.IsPinned;
        _storage.SetPin(item.Id, newPin);
        item.IsPinned = newPin;

        var menuItem = (System.Windows.Controls.MenuItem)sender;
        menuItem.Header = newPin ? "取消置顶" : "置顶";
        RefreshList(SearchBox.Text);
    }

    private void MenuDelete_Click(object sender, RoutedEventArgs e)
    {
        if (HistoryList.SelectedItem is not ClipboardItem item) return;
        _storage.Delete(item.Id);
        RefreshList(SearchBox.Text);
    }

    private void MenuClearAll_Click(object sender, RoutedEventArgs e)
    {
        _storage.ClearAll();
        RefreshList();
    }
}
