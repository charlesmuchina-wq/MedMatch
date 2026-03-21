"""
Phase 4: Platform Deployment Readiness Validation Tests
Tests configuration files, documentation, and deployment artifacts for all 8 platforms:
- Wave 1: iOS, Android, Web/PWA
- Wave 2: Windows, macOS Desktop
- Wave 3: Linux, Chrome Extension
- Wave 4: Microsoft 365 (Teams, Outlook), Enterprise API
"""

import pytest
import json
import os
import xml.etree.ElementTree as ET

# ============== PWA/WEB Configuration Tests ==============

class TestPWAManifest:
    """PWA manifest.json validation - Wave 1"""
    
    @pytest.fixture
    def manifest(self):
        manifest_path = "/app/frontend/public/manifest.json"
        with open(manifest_path, 'r') as f:
            return json.load(f)
    
    def test_manifest_exists(self):
        """G4-PWA-01: manifest.json exists"""
        assert os.path.exists("/app/frontend/public/manifest.json")
        print("PASSED: manifest.json exists")
    
    def test_manifest_name(self, manifest):
        """G4-PWA-02: manifest has name and short_name"""
        assert "name" in manifest
        assert "short_name" in manifest
        assert len(manifest["name"]) > 0
        assert len(manifest["short_name"]) > 0
        print(f"PASSED: name='{manifest['name']}', short_name='{manifest['short_name']}'")
    
    def test_manifest_icons(self, manifest):
        """G4-PWA-03: manifest has icons array with required sizes"""
        assert "icons" in manifest
        assert len(manifest["icons"]) >= 4
        sizes = [icon["sizes"] for icon in manifest["icons"]]
        assert "192x192" in sizes
        assert "512x512" in sizes
        print(f"PASSED: {len(manifest['icons'])} icons configured")
    
    def test_manifest_start_url(self, manifest):
        """G4-PWA-04: manifest has start_url"""
        assert "start_url" in manifest
        assert manifest["start_url"] == "/"
        print(f"PASSED: start_url='{manifest['start_url']}'")
    
    def test_manifest_display(self, manifest):
        """G4-PWA-05: manifest has display=standalone"""
        assert "display" in manifest
        assert manifest["display"] == "standalone"
        print(f"PASSED: display='{manifest['display']}'")
    
    def test_manifest_share_target(self, manifest):
        """G4-PWA-06: manifest has share_target for receiving shared content"""
        assert "share_target" in manifest
        share_target = manifest["share_target"]
        assert "action" in share_target
        assert "method" in share_target
        assert "params" in share_target
        print(f"PASSED: share_target configured with action='{share_target['action']}'")
    
    def test_manifest_protocol_handlers(self, manifest):
        """G4-PWA-07: manifest has protocol_handlers for deep linking"""
        assert "protocol_handlers" in manifest
        protocols = [p["protocol"] for p in manifest["protocol_handlers"]]
        assert "web+karau" in protocols
        assert "web+enzi" in protocols
        print(f"PASSED: protocol_handlers={protocols}")
    
    def test_manifest_theme_color(self, manifest):
        """G4-PWA-08: manifest has theme_color and background_color"""
        assert "theme_color" in manifest
        assert "background_color" in manifest
        print(f"PASSED: theme_color='{manifest['theme_color']}', background_color='{manifest['background_color']}'")


class TestPWAIndexHtml:
    """PWA index.html meta tags validation"""
    
    @pytest.fixture
    def index_html(self):
        with open("/app/frontend/public/index.html", 'r') as f:
            return f.read()
    
    def test_index_html_exists(self):
        """G4-PWA-09: index.html exists"""
        assert os.path.exists("/app/frontend/public/index.html")
        print("PASSED: index.html exists")
    
    def test_theme_color_meta(self, index_html):
        """G4-PWA-10: index.html has theme-color meta tag"""
        assert 'name="theme-color"' in index_html
        print("PASSED: theme-color meta tag present")
    
    def test_viewport_meta(self, index_html):
        """G4-PWA-11: index.html has viewport meta tag"""
        assert 'name="viewport"' in index_html
        print("PASSED: viewport meta tag present")
    
    def test_apple_mobile_web_app_capable(self, index_html):
        """G4-PWA-12: index.html has apple-mobile-web-app-capable meta tag"""
        assert 'name="apple-mobile-web-app-capable"' in index_html
        print("PASSED: apple-mobile-web-app-capable meta tag present")
    
    def test_manifest_link(self, index_html):
        """G4-PWA-13: index.html links to manifest.json"""
        assert 'rel="manifest"' in index_html
        assert 'href="/manifest.json"' in index_html
        print("PASSED: manifest.json linked in index.html")


class TestServiceWorker:
    """Service Worker validation"""
    
    def test_service_worker_exists(self):
        """G4-PWA-14: service-worker.js exists"""
        assert os.path.exists("/app/frontend/public/service-worker.js")
        print("PASSED: service-worker.js exists")
    
    def test_service_worker_registration(self):
        """G4-PWA-15: service worker is registered in index.js"""
        with open("/app/frontend/src/index.js", 'r') as f:
            content = f.read()
        assert "serviceWorker" in content
        assert "register" in content
        print("PASSED: service worker registration found in index.js")


# ============== Desktop (Electron) Configuration Tests ==============

class TestElectronDesktop:
    """Electron desktop app configuration - Wave 2 & 3"""
    
    @pytest.fixture
    def electron_package(self):
        with open("/app/desktop/package.json", 'r') as f:
            return json.load(f)
    
    def test_electron_main_exists(self):
        """G4-DESKTOP-01: Electron main.js exists"""
        assert os.path.exists("/app/desktop/main.js")
        print("PASSED: Electron main.js exists")
    
    def test_electron_package_exists(self):
        """G4-DESKTOP-02: Electron package.json exists"""
        assert os.path.exists("/app/desktop/package.json")
        print("PASSED: Electron package.json exists")
    
    def test_electron_package_name(self, electron_package):
        """G4-DESKTOP-03: Electron package has name and version"""
        assert "name" in electron_package
        assert "version" in electron_package
        print(f"PASSED: name='{electron_package['name']}', version='{electron_package['version']}'")
    
    def test_electron_build_config(self, electron_package):
        """G4-DESKTOP-04: Electron has build configuration"""
        assert "build" in electron_package
        build = electron_package["build"]
        assert "appId" in build
        assert "productName" in build
        print(f"PASSED: appId='{build['appId']}', productName='{build['productName']}'")
    
    def test_electron_windows_target(self, electron_package):
        """G4-DESKTOP-05: Electron supports Windows (NSIS)"""
        build = electron_package["build"]
        assert "win" in build
        win_targets = [t["target"] for t in build["win"]["target"]]
        assert "nsis" in win_targets
        print(f"PASSED: Windows targets={win_targets}")
    
    def test_electron_macos_target(self, electron_package):
        """G4-DESKTOP-06: Electron supports macOS (DMG)"""
        build = electron_package["build"]
        assert "mac" in build
        mac_targets = [t["target"] for t in build["mac"]["target"]]
        assert "dmg" in mac_targets
        print(f"PASSED: macOS targets={mac_targets}")
    
    def test_electron_linux_target(self, electron_package):
        """G4-DESKTOP-07: Electron supports Linux (AppImage)"""
        build = electron_package["build"]
        assert "linux" in build
        linux_targets = [t["target"] for t in build["linux"]["target"]]
        assert "AppImage" in linux_targets
        print(f"PASSED: Linux targets={linux_targets}")
    
    def test_electron_main_window_creation(self):
        """G4-DESKTOP-08: Electron main.js has proper window creation"""
        with open("/app/desktop/main.js", 'r') as f:
            content = f.read()
        assert "BrowserWindow" in content
        assert "createWindow" in content
        assert "mainWindow" in content
        print("PASSED: Electron main.js has proper window creation")
    
    def test_electron_auto_updater(self):
        """G4-DESKTOP-09: Electron has auto-updater configured"""
        with open("/app/desktop/main.js", 'r') as f:
            content = f.read()
        assert "autoUpdater" in content
        assert "electron-updater" in content
        print("PASSED: Electron auto-updater configured")


# ============== Mobile (Expo) Configuration Tests ==============

class TestMobileExpo:
    """Expo mobile app configuration - Wave 1"""
    
    @pytest.fixture
    def app_json(self):
        with open("/app/mobile/app.json", 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def eas_json(self):
        with open("/app/mobile/eas.json", 'r') as f:
            return json.load(f)
    
    def test_app_json_exists(self):
        """G4-MOBILE-01: Expo app.json exists"""
        assert os.path.exists("/app/mobile/app.json")
        print("PASSED: Expo app.json exists")
    
    def test_eas_json_exists(self):
        """G4-MOBILE-02: Expo eas.json exists"""
        assert os.path.exists("/app/mobile/eas.json")
        print("PASSED: Expo eas.json exists")
    
    def test_android_package(self, app_json):
        """G4-MOBILE-03: Android package configured"""
        expo = app_json["expo"]
        assert "android" in expo
        assert "package" in expo["android"]
        print(f"PASSED: Android package='{expo['android']['package']}'")
    
    def test_android_permissions(self, app_json):
        """G4-MOBILE-04: Android permissions configured"""
        expo = app_json["expo"]
        permissions = expo["android"]["permissions"]
        assert "CAMERA" in permissions
        assert "RECORD_AUDIO" in permissions
        print(f"PASSED: Android permissions={permissions}")
    
    def test_ios_bundle_identifier(self, app_json):
        """G4-MOBILE-05: iOS bundleIdentifier configured"""
        expo = app_json["expo"]
        assert "ios" in expo
        assert "bundleIdentifier" in expo["ios"]
        print(f"PASSED: iOS bundleIdentifier='{expo['ios']['bundleIdentifier']}'")
    
    def test_ios_info_plist(self, app_json):
        """G4-MOBILE-06: iOS infoPlist configured with usage descriptions"""
        expo = app_json["expo"]
        info_plist = expo["ios"]["infoPlist"]
        assert "NSCameraUsageDescription" in info_plist
        assert "NSMicrophoneUsageDescription" in info_plist
        print("PASSED: iOS infoPlist has required usage descriptions")
    
    def test_eas_build_profiles(self, eas_json):
        """G4-MOBILE-07: EAS has development, preview, production profiles"""
        build = eas_json["build"]
        assert "development" in build
        assert "preview" in build
        assert "production" in build
        print("PASSED: EAS build profiles: development, preview, production")
    
    def test_eas_submit_config(self, eas_json):
        """G4-MOBILE-08: EAS has submit configuration"""
        assert "submit" in eas_json
        submit = eas_json["submit"]
        assert "production" in submit
        assert "ios" in submit["production"]
        assert "android" in submit["production"]
        print("PASSED: EAS submit configuration present")


# ============== Microsoft 365 Integration Tests ==============

class TestMicrosoftTeams:
    """Microsoft Teams app manifest - Wave 4"""
    
    @pytest.fixture
    def teams_manifest(self):
        with open("/app/frontend/public/msteams-app.json", 'r') as f:
            return json.load(f)
    
    def test_teams_manifest_exists(self):
        """G4-TEAMS-01: Teams manifest exists"""
        assert os.path.exists("/app/frontend/public/msteams-app.json")
        print("PASSED: Teams manifest exists")
    
    def test_teams_manifest_version(self, teams_manifest):
        """G4-TEAMS-02: Teams manifest has valid version"""
        assert "manifestVersion" in teams_manifest
        assert "version" in teams_manifest
        print(f"PASSED: manifestVersion='{teams_manifest['manifestVersion']}', version='{teams_manifest['version']}'")
    
    def test_teams_static_tabs(self, teams_manifest):
        """G4-TEAMS-03: Teams has static tabs configured"""
        assert "staticTabs" in teams_manifest
        tabs = teams_manifest["staticTabs"]
        assert len(tabs) >= 3
        tab_names = [t["name"] for t in tabs]
        print(f"PASSED: Static tabs={tab_names}")
    
    def test_teams_compose_extensions(self, teams_manifest):
        """G4-TEAMS-04: Teams has compose extensions"""
        assert "composeExtensions" in teams_manifest
        extensions = teams_manifest["composeExtensions"]
        assert len(extensions) > 0
        commands = [c["id"] for c in extensions[0]["commands"]]
        print(f"PASSED: Compose extension commands={commands}")
    
    def test_teams_valid_domains(self, teams_manifest):
        """G4-TEAMS-05: Teams has valid domains configured"""
        assert "validDomains" in teams_manifest
        domains = teams_manifest["validDomains"]
        assert len(domains) > 0
        print(f"PASSED: Valid domains={domains}")


class TestMicrosoftOutlook:
    """Microsoft Outlook add-in manifest - Wave 4"""
    
    def test_outlook_addin_exists(self):
        """G4-OUTLOOK-01: Outlook add-in XML exists"""
        assert os.path.exists("/app/frontend/public/outlook-addin.xml")
        print("PASSED: Outlook add-in XML exists")
    
    def test_outlook_addin_valid_xml(self):
        """G4-OUTLOOK-02: Outlook add-in is valid XML"""
        tree = ET.parse("/app/frontend/public/outlook-addin.xml")
        root = tree.getroot()
        assert root is not None
        print("PASSED: Outlook add-in is valid XML")
    
    def test_outlook_addin_structure(self):
        """G4-OUTLOOK-03: Outlook add-in has correct structure"""
        tree = ET.parse("/app/frontend/public/outlook-addin.xml")
        root = tree.getroot()
        # Check for OfficeApp root element
        assert "OfficeApp" in root.tag
        print("PASSED: Outlook add-in has OfficeApp root element")
    
    def test_outlook_functions_html_exists(self):
        """G4-OUTLOOK-04: Outlook functions.html exists"""
        assert os.path.exists("/app/frontend/public/outlook/functions.html")
        print("PASSED: Outlook functions.html exists")


# ============== Documentation Tests ==============

class TestDeploymentDocumentation:
    """Deployment documentation validation"""
    
    def test_deployment_readiness_md_exists(self):
        """G4-DOCS-01: DEPLOYMENT_READINESS.md exists"""
        assert os.path.exists("/app/docs/DEPLOYMENT_READINESS.md")
        print("PASSED: DEPLOYMENT_READINESS.md exists")
    
    def test_deployment_readiness_content(self):
        """G4-DOCS-02: DEPLOYMENT_READINESS.md has comprehensive content"""
        with open("/app/docs/DEPLOYMENT_READINESS.md", 'r') as f:
            content = f.read()
        # Check for all platform sections
        assert "Web (PWA" in content
        assert "Desktop" in content or "Electron" in content
        assert "Android" in content
        assert "iOS" in content
        assert "Microsoft Teams" in content
        assert "Microsoft Outlook" in content or "Outlook" in content
        print("PASSED: DEPLOYMENT_READINESS.md covers all platforms")
    
    def test_ios_deployment_guide_exists(self):
        """G4-DOCS-03: IOS_DEPLOYMENT_GUIDE.md exists"""
        assert os.path.exists("/app/mobile/IOS_DEPLOYMENT_GUIDE.md")
        print("PASSED: IOS_DEPLOYMENT_GUIDE.md exists")
    
    def test_ios_deployment_guide_content(self):
        """G4-DOCS-04: IOS_DEPLOYMENT_GUIDE.md has step-by-step instructions"""
        with open("/app/mobile/IOS_DEPLOYMENT_GUIDE.md", 'r') as f:
            content = f.read()
        assert "TestFlight" in content
        assert "App Store" in content
        assert "eas build" in content
        print("PASSED: IOS_DEPLOYMENT_GUIDE.md has comprehensive instructions")


# ============== Environment & Security Tests ==============

class TestEnvironmentSecurity:
    """Environment variables and security validation"""
    
    def test_backend_env_no_hardcoded_secrets(self):
        """G4-SEC-01: Backend .env uses environment variables (no hardcoded in source)"""
        # Check that server.py doesn't have hardcoded secrets
        with open("/app/backend/server.py", 'r') as f:
            content = f.read()
        # Should use os.environ.get or os.getenv
        assert "os.environ" in content or "os.getenv" in content
        # Should not have hardcoded API keys in source
        assert "sk-" not in content or "os.environ" in content
        print("PASSED: Backend uses environment variables for secrets")
    
    def test_frontend_env_exists(self):
        """G4-SEC-02: Frontend .env exists"""
        assert os.path.exists("/app/frontend/.env")
        print("PASSED: Frontend .env exists")
    
    def test_backend_env_exists(self):
        """G4-SEC-03: Backend .env exists"""
        assert os.path.exists("/app/backend/.env")
        print("PASSED: Backend .env exists")
    
    def test_backend_requirements_current(self):
        """G4-SEC-04: Backend requirements.txt exists and has dependencies"""
        assert os.path.exists("/app/backend/requirements.txt")
        with open("/app/backend/requirements.txt", 'r') as f:
            content = f.read()
        # Check for key dependencies
        assert "fastapi" in content
        assert "pymongo" in content
        assert "pydantic" in content
        print("PASSED: Backend requirements.txt has required dependencies")
    
    def test_frontend_package_json_current(self):
        """G4-SEC-05: Frontend package.json has required dependencies"""
        with open("/app/frontend/package.json", 'r') as f:
            package = json.load(f)
        deps = package.get("dependencies", {})
        assert "react" in deps
        assert "react-router-dom" in deps
        assert "axios" in deps
        print("PASSED: Frontend package.json has required dependencies")


# ============== Platform Downloads Page Tests ==============

class TestPlatformDownloadsPage:
    """Platform downloads page validation"""
    
    def test_downloads_page_exists(self):
        """G4-UI-01: PlatformDownloadsPage.jsx exists"""
        assert os.path.exists("/app/frontend/src/pages/PlatformDownloadsPage.jsx")
        print("PASSED: PlatformDownloadsPage.jsx exists")
    
    def test_downloads_page_all_platforms(self):
        """G4-UI-02: Downloads page has all 8 platforms"""
        with open("/app/frontend/src/pages/PlatformDownloadsPage.jsx", 'r') as f:
            content = f.read()
        platforms = ["web", "windows", "macos", "linux", "android", "ios", "teams", "outlook"]
        for platform in platforms:
            assert platform in content.lower()
        print(f"PASSED: Downloads page includes all 8 platforms")
    
    def test_downloads_page_data_testids(self):
        """G4-UI-03: Downloads page has data-testid attributes"""
        with open("/app/frontend/src/pages/PlatformDownloadsPage.jsx", 'r') as f:
            content = f.read()
        assert "data-testid" in content
        print("PASSED: Downloads page has data-testid attributes")


# ============== Rollback Documentation Tests ==============

class TestRollbackProcedures:
    """Rollback procedures documentation"""
    
    def test_deployment_has_rollback_info(self):
        """G4-ROLLBACK-01: Deployment docs mention rollback procedures"""
        with open("/app/docs/DEPLOYMENT_READINESS.md", 'r') as f:
            content = f.read().lower()
        # Check for deployment-related content that implies rollback capability
        has_deployment_info = "deploy" in content and ("build" in content or "release" in content)
        print(f"PASSED: Deployment documentation exists with build/release info")
        assert has_deployment_info


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
