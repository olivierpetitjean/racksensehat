namespace NetApi.Infrastructure.Configuration;

public static class SharedConfigPathResolver
{
    public static string Resolve()
    {
        var envPath = Environment.GetEnvironmentVariable("THERMALGUARD_HAT_CONFIG_PATH");
        if (!string.IsNullOrWhiteSpace(envPath))
        {
            return envPath;
        }

        var cwd = Directory.GetCurrentDirectory();
        return Path.GetFullPath(Path.Combine(cwd, "..", "config", "settings.json"));
    }
}
