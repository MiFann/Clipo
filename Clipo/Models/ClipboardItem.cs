using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace Clipo.Models;

public enum ContentType { Text, Image, Files, Html }

public class ClipboardItem : INotifyPropertyChanged
{
    private string _displayText = "";
    private bool _isPinned;

    public int Id { get; set; }
    public string Content { get; set; } = "";
    public ContentType ContentType { get; set; } = ContentType.Text;
    public string ContentHash { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.Now;

    public bool IsPinned
    {
        get => _isPinned;
        set { _isPinned = value; OnPropertyChanged(); }
    }

    public string DisplayText
    {
        get => _displayText;
        set { _displayText = value; OnPropertyChanged(); }
    }

    public string TimeAgo => CreatedAt.ToString("MM-dd HH:mm");

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
