# KVG RGB - Feature TODO List

## Current Status
✅ Basic color control working
✅ Device and zone selection working
✅ Device/zone exclusion working
✅ SQLite database for persistent colors
✅ Zone checkbox behavior fixed
✅ UI spacing and margins polished
✅ Zone flash feature (works for multi-zone devices)
✅ Multi-mode support (Direct/Custom/Static)
✅ Friendly zone names
✅ Zone resize controls
✅ Per-zone brightness & saturation sliders
✅ Per-zone effects (rainbow, breathing, wave, cycle, static)
✅ Two-column UI layout with sticky color controls
✅ Full-width color picker with visible sliders
✅ Selection counting (devices, zones, LEDs)
✅ Per-zone color picker buttons
✅ UI reorganization (selection status, Reset All button)
✅ Old effects section removed
✅ Selection status pipe-delimited format (Task 1)
✅ Recent colors section with database persistence (Task 2)
✅ Device lock/toggle for zone controls (Task 3)
✅ Individual LED control & gradients (Task 4)

## Known Issues

### Flash Feature Limitations ⚠️
**Issue**: Zone flash and individual LED flash don't work properly on keyboards
- Flash functionality works fine on other devices (motherboards, etc.)
- Keyboard zones/LEDs don't visibly flash when triggered
- Likely due to keyboard firmware/driver handling
- **Workaround**: Use for non-keyboard devices only
- **Priority**: LOW - Device-specific limitation
- **Status**: DOCUMENTED, not fixing for now

## Planned Features

### 1. Configuration Profiles 💾
**Purpose**: Save and load different color configurations
- Save entire device/zone/LED configurations as named profiles
- Profiles should be nestable (device-level, zone-level, overall)
- Quick switching between profiles (Gaming, Work, Relaxing, etc.)
- Export/import profiles for sharing
- **Priority**: HIGH - Frequently requested feature
- **Status**: TODO

### 2. Favorite Colors & Gradients ⭐
**Purpose**: Quick access to frequently used colors and gradients
- Save favorite individual colors (beyond recent colors)
- Save favorite gradient combinations with names
- Organize in favorites section with custom names/tags
- **Priority**: MEDIUM - Nice UX enhancement
- **Status**: TODO

### 3. Pre-made Gradient Library 🌈
**Purpose**: Quick gradient selection without manual color picking
- Pre-defined gradients: Rainbow, Fire, Ocean, Sunset, Purple-Blue, etc.
- Visual preview of each gradient
- Click to apply to selected zone
- Expandable library
- **Priority**: MEDIUM - Good visual appeal
- **Status**: TODO

### Future Enhancements 🚀
**Ideas for future development**:
- LED pattern library (save/load custom LED patterns)
- Scheduling (time-based color changes)
- Integration with other apps (game events, music visualization, etc.)
- **Priority**: Future consideration
- **Status**: Ideas only

## Implementation Order (Next Steps)

### All Current Tasks Complete! ✅
All planned features from Tasks 1-4 have been implemented:
- ✅ Task 1: Pipe-delimited selection status
- ✅ Task 2: Recent colors with database
- ✅ Task 3: Device lock/toggle
- ✅ Task 4: Individual LED control & gradients

### Ready for Future Development 🚀
Next features will be determined based on user feedback and needs.

## Technical Notes

### Completed Database Schema
```sql
-- ✅ Colors table with all fields
CREATE TABLE colors (
    device_index INTEGER,
    zone_index INTEGER,
    r INTEGER,
    g INTEGER,
    b INTEGER,
    friendly_name TEXT,
    brightness INTEGER DEFAULT 100,
    saturation INTEGER DEFAULT 100,
    PRIMARY KEY (device_index, zone_index)
);

-- ✅ Effects table
CREATE TABLE effects (
    device_index INTEGER,
    zone_index INTEGER,
    effect_type TEXT,
    effect_params TEXT,
    PRIMARY KEY (device_index, zone_index)
);

-- ✅ Recent colors table
CREATE TABLE recent_colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    r INTEGER,
    g INTEGER,
    b INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ✅ LED colors table (individual LED control)
CREATE TABLE led_colors (
    device_index INTEGER,
    zone_index INTEGER,
    led_index INTEGER,
    r INTEGER,
    g INTEGER,
    b INTEGER,
    PRIMARY KEY (device_index, zone_index, led_index)
);

-- ✅ LED control enabled state
CREATE TABLE led_control_enabled (
    device_index INTEGER,
    zone_index INTEGER,
    enabled INTEGER DEFAULT 0,
    PRIMARY KEY (device_index, zone_index)
);
```

### Completed API Endpoints
- ✅ `POST /api/zone/flash` - Flash zone for identification
- ✅ `POST /api/zone/resize` - Resize zone LED count
- ✅ `POST /api/zone/rename` - Set friendly name
- ✅ `POST /api/zone/brightness` - Set brightness/saturation
- ✅ `POST /api/zone/effect` - Set zone effect
- ✅ `POST /api/zone/color` - Set zone color
- ✅ `POST /api/device/lock` - Toggle device lock state
- ✅ `GET /api/device/locks` - Get all device lock states
- ✅ `GET /api/colors/recent` - Get recent custom colors
- ✅ `POST /api/colors/recent` - Save recent custom color
- ✅ `GET /api/zone/<device>/<zone>/leds` - Get LED colors and state
- ✅ `POST /api/zone/<device>/<zone>/led/<led>/color` - Set individual LED color
- ✅ `POST /api/zone/<device>/<zone>/led/<led>/flash` - Flash individual LED
- ✅ `POST /api/zone/<device>/<zone>/gradient` - Apply gradient to zone LEDs
- ✅ `POST /api/zone/<device>/<zone>/leds/fill` - Set all LEDs to same color (fast)
- ✅ `POST /api/zone/<device>/<zone>/leds/clear` - Clear LED colors
- ✅ `POST /api/zone/<device>/<zone>/leds/toggle` - Toggle LED control on/off

---

**Ready to commit current changes and then tackle the new features!**
