# Release Process

This document describes the automated release process for GeoPublicHealth.

## Automated Release (Recommended)

The project uses GitHub Actions to automate the build and release process.

### Creating a New Release

1. **Update version numbers** in:
   - `metadata.txt` - Update `version=version X.Y.Z`
   - `docs/plugins.xml` - Update `<version>X.Y.Z</version>` and download URL
   - `docs/plugins.xml` - Update `<update_date>` to current date

2. **Update changelog** in `metadata.txt`:
   ```
   changelog=The changelog lists the plugin versions
       and their changes:
       X.Y.Z - Description of changes
       ...
   ```

3. **Commit changes**:
   ```bash
   git add metadata.txt docs/plugins.xml
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

4. **Create and push a version tag**:
   ```bash
   git tag -a vX.Y.Z -m "Version X.Y.Z - Brief description"
   git push origin vX.Y.Z
   ```

5. **GitHub Actions will automatically**:
   - Build the plugin package
   - Create a GitHub release
   - Attach the zip file to the release
   - Generate release notes

6. **Verify the release**:
   ```bash
   gh release view vX.Y.Z --repo ePublicHealth/GeoPublicHealth
   ```

## Manual Release (Fallback)

If you need to create a release manually:

### 1. Build the Plugin Package

```bash
# Create build directory
mkdir -p build/GeoPublicHealth

# Copy plugin files (exclude development files)
rsync -av \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='installation' \
  --exclude='.tx' \
  --exclude='.github' \
  --exclude='.travis.yml' \
  --exclude='Makefile' \
  --exclude='test_suite.py' \
  --exclude='CONTRIBUTING.md' \
  --exclude='videos' \
  --exclude='docs' \
  --exclude='scripts' \
  --exclude='sample_data' \
  --exclude='AGENTS.md' \
  --exclude='*.log' \
  --exclude='.vscode' \
  --exclude='.ruff_cache' \
  --exclude='.gitignore' \
  --exclude='build' \
  ./ build/GeoPublicHealth/

# Create zip file
cd build
zip -r geopublichealth3.42.X.zip GeoPublicHealth -x "*.pyc" "*__pycache__*" "*.DS_Store"
cd ..
```

### 2. Add to Installation Directory

```bash
# Copy to installation directory (tracked in git)
cp build/geopublichealth3.42.X.zip installation/

# Add to git (use -f since installation/ is in .gitignore)
git add -f installation/geopublichealth3.42.X.zip
```

### 3. Create GitHub Release

```bash
# Create git tag
git tag -a vX.Y.Z -m "Version X.Y.Z - Description"
git push origin vX.Y.Z

# Create GitHub release with gh CLI
gh release create vX.Y.Z \
  installation/geopublichealth3.42.X.zip \
  --repo ePublicHealth/GeoPublicHealth \
  --title "GeoPublicHealth vX.Y.Z" \
  --notes "Release notes here..."
```

## Version Numbering

Follow Semantic Versioning (https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.2.1)
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward compatible manner
- **PATCH**: Backward compatible bug fixes

Examples:
- `0.2.0` → `0.2.1` - Bug fix release
- `0.2.1` → `0.3.0` - New features added
- `0.3.0` → `1.0.0` - Stable release or breaking changes

## Testing Before Release

Before creating a release, always:

1. **Run PEP8 checks**:
   ```bash
   make pep8
   ```

2. **Run tests**:
   ```bash
   python test_suite.py
   ```

3. **Test the plugin in QGIS**:
   - Install from the built zip file
   - Test core functionality
   - Check for errors in QGIS logs

## Updating Plugin Repository

The plugin repository is defined in `docs/plugins.xml`. This file is served directly from GitHub and used by QGIS to check for updates.

When you create a new release:
1. Update the `<version>` tag
2. Update the `<download_url>` to point to the new zip file
3. Update the `<update_date>` to the current date
4. Commit and push these changes

QGIS will automatically detect the new version and offer it to users.

## Rollback

If you need to rollback a release:

1. Delete the GitHub release:
   ```bash
   gh release delete vX.Y.Z --repo ePublicHealth/GeoPublicHealth --yes
   ```

2. Delete the tag:
   ```bash
   git tag -d vX.Y.Z
   git push origin :refs/tags/vX.Y.Z
   ```

3. Revert version changes in metadata files and commit

## CI/CD Workflows

The project includes two GitHub Actions workflows:

### 1. `build-and-release.yml`
- **Trigger**: Push to version tags (`v*`)
- **Actions**:
  - Builds plugin package
  - Creates GitHub release
  - Attaches zip file to release
- **Manual trigger**: Can be run manually from Actions tab

### 2. `test.yml`
- **Trigger**: Push to main/develop, Pull requests
- **Actions**:
  - Runs PEP8 checks
  - Validates Python syntax
  - Lists project files

## Troubleshooting

### GitHub Actions not triggering
- Ensure the tag starts with 'v' (e.g., `v0.2.1`)
- Check workflow permissions in repository settings

### Release creation fails
- Verify GitHub token has write permissions
- Check that the tag exists: `git tag -l`

### Zip file too large
- Ensure build excludes unnecessary files (tests, docs, etc.)
- Check for accidentally included binary files

### Plugin not updating in QGIS
- Verify `plugins.xml` has correct download URL
- Clear QGIS plugin cache
- Check QGIS repository settings
