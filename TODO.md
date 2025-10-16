# KVG RGB - Feature TODO List

## Current Status
✅ Basic color control working
✅ Device and zone selection working
✅ Device/zone exclusion working
✅ SQLite database for persistent colors
✅ Zone checkbox behavior fixed
✅ UI spacing and margins polished

## Planned Features

### 1. Zone Flash/Identification ⏳
**Purpose**: Help users visually identify which physical LED corresponds to which zone
- Add "Flash" button to each zone
- When clicked, flash that zone white/bright color for 2-3 seconds
- Then restore previous color
- **Priority**: HIGH - Very useful for setup

### 2. Friendly Zone Names ⏳
**Purpose**: Let users rename zones to meaningful names (e.g., "CPU Header" instead of "Addressable 1")
- Add `friendly_name` field to database
- Add text input/edit button next to zone name
- Display friendly name in UI (with original name as subtitle)
- Store in config or database
- **Priority**: MEDIUM - Nice quality of life feature

### 3. Zone Resize Controls ⏳
**Purpose**: Allow users to adjust the number of LEDs in resizable zones
- Already have resize button (⚙️) for resizable zones
- Currently shows dialog - need to implement backend
- Add API endpoint `/api/zone/resize`
- Update OpenRGB zone size via SDK
- **Priority**: MEDIUM - Some users need this

### 4. Individual LED Control & Gradients ⏳
**Purpose**: Fine-grained control for advanced effects
- Add "Advanced" mode for each zone
- Show individual LED grid/list
- Color picker for each LED
- Gradient generator (start color → end color)
- Pattern options (alternating, wave, etc.)
- **Priority**: LOW - Advanced feature, can wait

### 5. Brightness & Saturation Controls ⏳
**Purpose**: Adjust color intensity without changing hue
- Add brightness slider per device/zone (0-100%)
- Add saturation slider per device/zone (0-100%)
- Apply to color picker output
- Store in database with colors
- **Priority**: MEDIUM - Common request

### 6. Per-Device/Zone Effects ⏳
**Purpose**: Apply animated effects to specific devices or zones
- Currently have rainbow and breathing effects (global only)
- Add effect selector per device/zone
- Effects: Static, Rainbow, Breathing, Wave, Cycle
- Effect parameters (speed, direction, etc.)
- Store active effects in database
- **Priority**: MEDIUM-LOW - Cool but not essential

## Implementation Order (Suggested)

### Phase 1 - Quick Wins 🎯
1. **Zone Flash** - Easy to implement, very useful
2. **Zone Resize Backend** - Dialog already exists, just needs API

### Phase 2 - Quality of Life 🎨
3. **Friendly Zone Names** - Makes UI more user-friendly
4. **Brightness/Saturation** - Common feature request

### Phase 3 - Advanced Features 🚀
5. **Per-Device/Zone Effects** - More complex, requires effect management
6. **Individual LED Control** - Most complex, advanced users only

## Technical Notes

### Database Schema Updates Needed
```sql
-- For friendly names
ALTER TABLE colors ADD COLUMN friendly_name TEXT;

-- For brightness/saturation
ALTER TABLE colors ADD COLUMN brightness INTEGER DEFAULT 100;
ALTER TABLE colors ADD COLUMN saturation INTEGER DEFAULT 100;

-- For effects (new table)
CREATE TABLE effects (
    device_index INTEGER,
    zone_index INTEGER,
    effect_type TEXT,
    effect_params TEXT,
    PRIMARY KEY (device_index, zone_index)
);
```

### API Endpoints to Add
- `POST /api/zone/flash` - Flash zone for identification
- `POST /api/zone/resize` - Resize zone LED count
- `POST /api/zone/rename` - Set friendly name
- `POST /api/zone/led/{led_index}/color` - Set individual LED color
- `POST /api/effect/start` - Start effect on device/zone
- `POST /api/effect/stop` - Stop effect

### UI Components to Add
- Flash button (⚡) next to each zone
- Inline text edit for friendly names
- Brightness/saturation sliders in color control
- Effect selector dropdown
- LED grid view (collapsible, per zone)

---

**Let me know which feature you'd like to start with!** 

Recommendation: Start with **Zone Flash** - it's quick, easy, and immediately useful for identifying zones.
