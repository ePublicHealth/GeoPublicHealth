# Instructions to Fix GeoPublicHealth Installation

If you're seeing the error `ModuleNotFoundError: No module named 'GeoPublicHealth'`, you have an old cached version of the plugin installed.

## Step-by-Step Fix

### 1. Uninstall the Plugin in QGIS
1. Open QGIS
2. Go to **Plugins** → **Manage and Install Plugins...**
3. Click the **Installed** tab
4. Find **GeoPublicHealth** in the list
5. Click **Uninstall Plugin**
6. Close QGIS completely

### 2. Manually Delete the Plugin Directory
The uninstaller might not remove all files. Delete the plugin directory manually:

**On macOS:**
```bash
rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/geopublichealth
```

**On Windows:**
```cmd
rmdir /s /q "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\geopublichealth"
```

**On Linux:**
```bash
rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/geopublichealth
```

### 3. Clear QGIS Cache (Optional but Recommended)
**On macOS:**
```bash
rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/cache
```

**On Windows:**
```cmd
rmdir /s /q "%APPDATA%\QGIS\QGIS3\profiles\default\cache"
```

**On Linux:**
```bash
rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/cache
```

### 4. Restart QGIS

### 5. Reinstall the Plugin
1. Open QGIS
2. Go to **Plugins** → **Manage and Install Plugins...**
3. Go to the **Settings** tab
4. Click **Reload all repositories** (this ensures you get the latest version)
5. Go to the **All** tab
6. Search for **geopublichealth**
7. Select it and click **Install Plugin**

The plugin should now install correctly with the updated code!

## Verification

After installation, check that the plugin loaded successfully:
1. Go to **Plugins** → **Manage and Install Plugins...**
2. Click the **Installed** tab
3. **GeoPublicHealth** should be listed without any error icons
4. You should see the **GeoPublicHealth** menu in the QGIS menu bar

## Still Having Issues?

If you're still experiencing problems:
1. Check the QGIS Python console for error messages: **Plugins** → **Python Console**
2. Verify the plugin directory contents:
   ```bash
   ls -la ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/geopublichealth/
   ```
3. Make sure the `__init__.py` file contains: `from geopublichealth.src.plugin import GeoPublicHealthPlugin`

## For Developers

If you're developing or testing locally, make sure to:
1. Always use the lowercase `geopublichealth` in all imports
2. The plugin directory must be named `geopublichealth` (lowercase)
3. Rebuild the zip file after any code changes
