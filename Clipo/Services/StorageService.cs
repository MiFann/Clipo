using System.IO;
using Microsoft.Data.Sqlite;
using Clipo.Models;

namespace Clipo.Services;

public class StorageService : IDisposable
{
    private readonly SqliteConnection _db;

    public StorageService()
    {
        var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Clipo");
        Directory.CreateDirectory(dir);
        var dbPath = Path.Combine(dir, "clipo.db");

        _db = new SqliteConnection($"Data Source={dbPath}");
        _db.Open();

        using var cmd = _db.CreateCommand();
        cmd.CommandText = """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL DEFAULT 'Text',
                content_hash TEXT NOT NULL,
                is_pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_history_hash ON history(content_hash);
            CREATE INDEX IF NOT EXISTS idx_history_time ON history(created_at DESC);
            """;
        cmd.ExecuteNonQuery();
    }

    public ClipboardItem? GetLast()
    {
        using var cmd = _db.CreateCommand();
        cmd.CommandText = "SELECT * FROM history ORDER BY created_at DESC LIMIT 1";
        return ReadItem(cmd);
    }

    public void Upsert(string content, ContentType type, string hash)
    {
        using var txn = _db.BeginTransaction();

        // If same hash as last entry, just update timestamp
        var last = GetLast();
        if (last != null && last.ContentHash == hash)
        {
            using var upd = _db.CreateCommand();
            upd.CommandText = "UPDATE history SET created_at = datetime('now','localtime') WHERE id = @id";
            upd.Parameters.AddWithValue("@id", last.Id);
            upd.ExecuteNonQuery();
            txn.Commit();
            return;
        }

        // Insert new entry
        using var ins = _db.CreateCommand();
        ins.CommandText = "INSERT INTO history (content, content_type, content_hash) VALUES (@c, @t, @h)";
        ins.Parameters.AddWithValue("@c", content);
        ins.Parameters.AddWithValue("@t", type.ToString());
        ins.Parameters.AddWithValue("@h", hash);
        ins.ExecuteNonQuery();

        // Keep max 200 items
        using var del = _db.CreateCommand();
        del.CommandText = """
            DELETE FROM history WHERE id NOT IN (
                SELECT id FROM history ORDER BY is_pinned DESC, created_at DESC LIMIT 200
            )
            """;
        del.ExecuteNonQuery();

        txn.Commit();
    }

    public List<ClipboardItem> Search(string? query = null, int limit = 100)
    {
        var items = new List<ClipboardItem>();
        using var cmd = _db.CreateCommand();

        if (string.IsNullOrWhiteSpace(query))
        {
            cmd.CommandText = "SELECT * FROM history ORDER BY is_pinned DESC, created_at DESC LIMIT @limit";
        }
        else
        {
            cmd.CommandText = "SELECT * FROM history WHERE content LIKE @q ORDER BY is_pinned DESC, created_at DESC LIMIT @limit";
            cmd.Parameters.AddWithValue("@q", $"%{query}%");
        }

        cmd.Parameters.AddWithValue("@limit", limit);

        using var reader = cmd.ExecuteReader();
        while (reader.Read())
            items.Add(MapItem(reader));

        return items;
    }

    public void Delete(int id)
    {
        using var cmd = _db.CreateCommand();
        cmd.CommandText = "DELETE FROM history WHERE id = @id";
        cmd.Parameters.AddWithValue("@id", id);
        cmd.ExecuteNonQuery();
    }

    public void SetPin(int id, bool pinned)
    {
        using var cmd = _db.CreateCommand();
        cmd.CommandText = "UPDATE history SET is_pinned = @p WHERE id = @id";
        cmd.Parameters.AddWithValue("@p", pinned ? 1 : 0);
        cmd.Parameters.AddWithValue("@id", id);
        cmd.ExecuteNonQuery();
    }

    public void ClearAll()
    {
        using var cmd = _db.CreateCommand();
        cmd.CommandText = "DELETE FROM history";
        cmd.ExecuteNonQuery();
    }

    private ClipboardItem? ReadItem(SqliteCommand cmd)
    {
        using var reader = cmd.ExecuteReader();
        if (reader.Read())
            return MapItem(reader);
        return null;
    }

    private static ClipboardItem MapItem(SqliteDataReader r) => new()
    {
        Id = r.GetInt32(0),
        Content = r.GetString(1),
        ContentType = Enum.TryParse<ContentType>(r.GetString(2), out var t) ? t : ContentType.Text,
        ContentHash = r.GetString(3),
        IsPinned = r.GetInt32(4) == 1,
        CreatedAt = DateTime.TryParse(r.GetString(5), out var dt) ? dt : DateTime.Now,
        DisplayText = TruncateText(r.GetString(1))
    };

    public static string TruncateText(string text, int maxLen = 120)
    {
        var line = text.Replace('\n', ' ').Replace('\r', ' ').Trim();
        return line.Length <= maxLen ? line : line[..maxLen] + "...";
    }

    public void Dispose() => _db?.Dispose();
}
