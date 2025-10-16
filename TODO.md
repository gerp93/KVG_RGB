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

## Planned Features

### 1. Selection Status Display Format 🎯
**Purpose**: Make selection status more compact
- Change selection count from multi-line to pipe-delimited format
- Example: "3 Devices | 7 Zones | 142 LEDs" (similar to device cards)
- Reduce vertical space in color control panel
- **Priority**: HIGH - Quick UI polish before commit
- **Status**: TODO

### 2. Recent Colors Section 🎨
**Purpose**: Quick access to recently used custom colors
- Add "Recent Colors" section under "Quick Colors"
- Store last 8-10 custom colors selected via color picker
- Display as color swatches (similar to quick colors)
- Click to apply recent color
- Persist in localStorage or database
- **Priority**: MEDIUM - Nice quality of life feature
- **Status**: TODO

### 3. Device Lock/Toggle for Zone Controls 🔒
**Purpose**: Simplify UI by treating entire device as single unit when desired
- Add lock/unlock toggle button on each device card
- **Locked Mode**: 
  - Show device-level controls (color picker, brightness, saturation, effect selector)
  - Apply changes to ALL zones at once
  - Hide individual zone controls completely
  - Don't display zone rows at all
- **Unlocked Mode** (current behavior):
  - Show all zones with individual controls
  - Per-zone color pickers, sliders, effect selectors
- Benefits: Cleaner UI for devices you want uniform, per-zone control when needed
- **Priority**: MEDIUM-HIGH - Significant UX improvement
- **Status**: TODO

### 4. Individual LED Control & Gradients ⏳
**Purpose**: Fine-grained control for advanced effects
- Add "Advanced" mode for each zone
- Show individual LED grid/list
- Color picker for each LED
- Gradient generator (start color → end color)
- Pattern options (alternating, wave, etc.)
- **Priority**: LOW - Advanced feature, can wait
- **Status**: TODO

## Implementation Order (Next Steps)

### Phase 1 - Pre-Commit Polish 🎯
1. **Selection Status Format** - Quick 5-minute change
2. Commit current UI improvements

### Phase 2 - Quality of Life Enhancements 🎨
3. **Recent Colors Section** - Moderate complexity, good UX
4. **Device Lock Toggle** - More complex, significant UX improvement

### Phase 3 - Advanced Features 🚀
5. **Individual LED Control** - Most complex, advanced users only

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
```

### Completed API Endpoints
- ✅ `POST /api/zone/flash` - Flash zone for identification
- ✅ `POST /api/zone/resize` - Resize zone LED count
- ✅ `POST /api/zone/rename` - Set friendly name
- ✅ `POST /api/zone/brightness` - Set brightness/saturation
- ✅ `POST /api/zone/effect` - Set zone effect
- ✅ `POST /api/zone/color` - Set zone color

### Future API Endpoints Needed
- `POST /api/device/lock` - Toggle device lock state
- `POST /api/device/color` - Set color for locked device (all zones)
- `POST /api/device/brightness` - Set brightness for locked device
- `POST /api/device/effect` - Set effect for locked device
- `GET /api/colors/recent` - Get recent custom colors
- `POST /api/colors/recent` - Save recent custom color
- `POST /api/zone/led/{led_index}/color` - Set individual LED color

---

**Ready to commit current changes and then tackle the new features!**
