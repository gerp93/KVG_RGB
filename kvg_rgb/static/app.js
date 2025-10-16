// Global state
let devices = [];
let currentEffect = null;
let selectedItems = []; // Array of {type: 'device'|'zone', deviceIndex, zoneIndex (optional)}
let recentColors = []; // Array of recent RGB colors
const MAX_RECENT_COLORS = 8; // Maximum number of recent colors to store

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRecentColors();
    loadDevices();
    setupEffectControls();
});

// Load devices from API
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        const data = await response.json();
        
        if (data.success) {
            devices = data.devices;
            displayDevices();
            updateStatus('✓ Connected to OpenRGB', 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to connect to OpenRGB server', 'error');
        console.error('Error loading devices:', error);
    }
}

// Display devices with selectable zones
function displayDevices() {
    const deviceList = document.getElementById('deviceList');
    
    // Separate enabled and disabled devices
    const enabledDevices = devices.filter(d => !d.excluded);
    const disabledDevices = devices.filter(d => d.excluded);
    
    // Render enabled devices
    const enabledHTML = enabledDevices.map(device => `
        <div class="device-card-vertical" id="device-card-${device.index}">
            <!-- Device Header (Selectable) -->
            <div class="device-header-selectable ${isDeviceSelected(device.index) ? 'selected' : ''}" 
                 onclick="toggleDeviceSelection(${device.index})"
                 data-device="${device.index}">
                <div class="selection-indicator">
                    <span class="checkbox">${isDeviceSelected(device.index) ? '☑' : '☐'}</span>
                </div>
                <div class="device-info-compact">
                    <div class="device-name-large">${device.name}</div>
                    <div class="device-stats">💡 ${device.leds} LEDs | 📦 ${device.zones.length} Zones</div>
                </div>
                <div class="device-actions">
                    <select class="effect-selector" 
                            onclick="event.stopPropagation()"
                            onchange="setDeviceEffect(${device.index}, this.value)"
                            title="Set effect for all zones">
                        <option value="">Set All Zones...</option>
                        <option value="static">Static</option>
                        <option value="rainbow">🌈 Rainbow</option>
                        <option value="breathing">💨 Breathing</option>
                        <option value="wave">🌊 Wave</option>
                        <option value="cycle">🔄 Cycle</option>
                    </select>
                    <button class="device-toggle-mini" 
                            onclick="event.stopPropagation(); toggleDevice('${device.name.replace(/'/g, "\\'")}', ${device.index})"
                            title="Disable this device">
                        🟢
                    </button>
                </div>
            </div>
            
            ${device.zones.length > 0 ? `
                <!-- Zones List -->
                <div class="zones-container">
                    ${device.zones.filter(z => !z.excluded).map((zone) => {
                        const originalZoneIndex = device.zones.indexOf(zone);
                        return `
                        <div class="zone-item-selectable ${isZoneSelected(device.index, originalZoneIndex) ? 'selected' : ''}"
                             data-device="${device.index}"
                             data-zone="${originalZoneIndex}">
                            <div class="zone-main-row" onclick="toggleZoneSelection(${device.index}, ${originalZoneIndex})">
                                <div class="selection-indicator">
                                    <span class="checkbox">${isZoneSelected(device.index, originalZoneIndex) ? '☑' : '☐'}</span>
                                </div>
                                <div class="zone-info-compact">
                                    <div class="zone-name-text">
                                        ${zone.friendly_name ? `
                                            <span class="zone-friendly-name">${zone.friendly_name}</span>
                                            <span class="zone-original-name">${zone.name}</span>
                                        ` : zone.name}
                                    </div>
                                    <div class="zone-led-count">${zone.leds} LEDs</div>
                                </div>
                                <div class="zone-actions">
                                    <input type="color" 
                                           class="color-picker-mini" 
                                           value="${zone.color ? rgbToHex(zone.color.r, zone.color.g, zone.color.b) : '#000000'}"
                                           onclick="event.stopPropagation()"
                                           onchange="setZoneColorFromPicker(${device.index}, ${originalZoneIndex}, this.value)"
                                           title="Zone color">
                                    <button class="btn-mini" 
                                            onclick="event.stopPropagation(); editZoneName(${device.index}, ${originalZoneIndex}, '${zone.name.replace(/'/g, "\\'")}', '${(zone.friendly_name || '').replace(/'/g, "\\'")}')"
                                            title="Rename zone">
                                        ✏️
                                    </button>
                                    <button class="btn-mini btn-flash" 
                                            onclick="event.stopPropagation(); flashZone(${device.index}, ${originalZoneIndex})"
                                            title="Flash zone to identify">
                                        ⚡
                                    </button>
                                    <select class="effect-selector" 
                                            onclick="event.stopPropagation()"
                                            onchange="setZoneEffect(${device.index}, ${originalZoneIndex}, this.value)"
                                            title="Zone effect">
                                        <option value="static" ${zone.effect === 'static' ? 'selected' : ''}>Static</option>
                                        <option value="rainbow" ${zone.effect === 'rainbow' ? 'selected' : ''}>🌈 Rainbow</option>
                                        <option value="breathing" ${zone.effect === 'breathing' ? 'selected' : ''}>💨 Breathing</option>
                                        <option value="wave" ${zone.effect === 'wave' ? 'selected' : ''}>🌊 Wave</option>
                                        <option value="cycle" ${zone.effect === 'cycle' ? 'selected' : ''}>🔄 Cycle</option>
                                    </select>
                                    ${zone.resizable ? `
                                        <button class="btn-mini" 
                                                onclick="event.stopPropagation(); showResizeDialog(${device.index}, ${originalZoneIndex}, ${zone.leds_min || 1}, ${zone.leds_max || 300}, ${zone.leds})"
                                                title="Resize zone (adjust LED count)">
                                            ⚙️
                                        </button>
                                    ` : ''}
                                    <button class="device-toggle-mini" 
                                            onclick="event.stopPropagation(); toggleZoneExclusion('${device.name.replace(/'/g, "\\'")}', ${device.index}, ${originalZoneIndex})"
                                            title="Disable this zone">
                                        🟢
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Zone Brightness/Saturation Controls -->
                            <div class="zone-sliders" onclick="event.stopPropagation()">
                                <div class="zone-slider-control">
                                    <label>💡</label>
                                    <input type="range" 
                                           min="0" 
                                           max="100" 
                                           value="${zone.brightness || 100}"
                                           class="zone-slider"
                                           oninput="updateZoneSliderValue(${device.index}, ${originalZoneIndex}, 'brightness', this.value)"
                                           onchange="applyZoneBrightnessSaturation(${device.index}, ${originalZoneIndex})"
                                           title="Brightness">
                                    <span class="zone-slider-value" id="zone-brightness-${device.index}-${originalZoneIndex}">${zone.brightness || 100}%</span>
                                </div>
                                <div class="zone-slider-control">
                                    <label>🎨</label>
                                    <input type="range" 
                                           min="0" 
                                           max="100" 
                                           value="${zone.saturation || 100}"
                                           class="zone-slider"
                                           oninput="updateZoneSliderValue(${device.index}, ${originalZoneIndex}, 'saturation', this.value)"
                                           onchange="applyZoneBrightnessSaturation(${device.index}, ${originalZoneIndex})"
                                           title="Saturation">
                                    <span class="zone-slider-value" id="zone-saturation-${device.index}-${originalZoneIndex}">${zone.saturation || 100}%</span>
                                </div>
                            </div>
                        </div>
                    `;
                    }).join('')}
                    
                    ${device.zones.filter(z => z.excluded).length > 0 ? `
                        <!-- Disabled Zones Section -->
                        <div class="disabled-zones-section">
                            <div class="disabled-zones-header" onclick="toggleDisabledZones(${device.index})">
                                <span class="collapse-icon" id="disabledZonesIcon-${device.index}">▶</span>
                                <span>Disabled Zones (${device.zones.filter(z => z.excluded).length})</span>
                            </div>
                            <div class="disabled-zones-list" id="disabledZonesList-${device.index}" style="display: none;">
                                ${device.zones.filter(z => z.excluded).map((zone) => {
                                    const originalZoneIndex = device.zones.indexOf(zone);
                                    return `
                                    <div class="zone-item-selectable zone-excluded"
                                         data-device="${device.index}"
                                         data-zone="${originalZoneIndex}">
                                        <div class="zone-info-compact">
                                            <div class="zone-name-text">${zone.name}</div>
                                            <div class="zone-led-count">${zone.leds} LEDs</div>
                                        </div>
                                        <div class="zone-actions">
                                            <button class="device-toggle-mini" 
                                                    onclick="event.stopPropagation(); toggleZoneExclusion('${device.name.replace(/'/g, "\\'")}', ${device.index}, ${originalZoneIndex})"
                                                    title="Enable this zone">
                                                🔴
                                            </button>
                                        </div>
                                    </div>
                                `;
                                }).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            ` : ''}
        </div>
    `).join('');
    
    // Render disabled devices in collapsible section
    const disabledHTML = disabledDevices.length > 0 ? `
        <div class="disabled-devices-section">
            <div class="disabled-devices-header" onclick="toggleDisabledDevices()">
                <span class="collapse-icon" id="disabledCollapseIcon">▶</span>
                <span>Disabled Devices (${disabledDevices.length})</span>
            </div>
            <div class="disabled-devices-list" id="disabledDevicesList" style="display: none;">
                ${disabledDevices.map(device => `
                    <div class="device-card-vertical excluded" id="device-card-${device.index}">
                        <div class="device-header-selectable" data-device="${device.index}">
                            <div class="device-info-compact">
                                <div class="device-name-large">${device.name}</div>
                                <div class="device-stats">💡 ${device.leds} LEDs | 📦 ${device.zones.length} Zones</div>
                            </div>
                            <button class="device-toggle-mini" 
                                    onclick="event.stopPropagation(); toggleDevice('${device.name.replace(/'/g, "\\'")}', ${device.index})"
                                    title="Enable this device">
                                🔴
                            </button>
                        </div>
                        <div class="device-disabled-msg">Click 🟢 to enable RGB control</div>
                    </div>
                `).join('')}
            </div>
        </div>
    ` : '';
    
    deviceList.innerHTML = enabledHTML + disabledHTML;
}

// Selection management
function isDeviceSelected(deviceIndex) {
    return selectedItems.some(item => item.type === 'device' && item.deviceIndex === deviceIndex);
}

function isZoneSelected(deviceIndex, zoneIndex) {
    // Zone is selected if it's explicitly selected OR if its parent device is selected
    return isDeviceSelected(deviceIndex) || 
           selectedItems.some(item => 
               item.type === 'zone' && 
               item.deviceIndex === deviceIndex && 
               item.zoneIndex === zoneIndex
           );
}

function toggleDeviceSelection(deviceIndex) {
    const device = devices[deviceIndex];
    if (device.excluded) return;
    
    if (isDeviceSelected(deviceIndex)) {
        // Deselect device and all its zones
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'device' && item.deviceIndex === deviceIndex)
        );
        // Also deselect all zones from this device
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'zone' && item.deviceIndex === deviceIndex)
        );
    } else {
        // Select device only (don't add zones - device selection covers all zones)
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'zone' && item.deviceIndex === deviceIndex)
        );
        selectedItems.push({ type: 'device', deviceIndex });
    }
    displayDevices();
    updateSelectionStatus();
}

function toggleZoneSelection(deviceIndex, zoneIndex) {
    const device = devices[deviceIndex];
    if (device.excluded) return;
    
    // Check if this specific zone is in selectedItems (not just appearing selected because device is selected)
    const zoneExplicitlySelected = selectedItems.some(item => 
        item.type === 'zone' && 
        item.deviceIndex === deviceIndex && 
        item.zoneIndex === zoneIndex
    );
    
    if (zoneExplicitlySelected) {
        // This zone is explicitly selected - uncheck just this zone
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'zone' && item.deviceIndex === deviceIndex && item.zoneIndex === zoneIndex)
        );
        // Also uncheck parent device if it's selected
        if (isDeviceSelected(deviceIndex)) {
            selectedItems = selectedItems.filter(item => 
                !(item.type === 'device' && item.deviceIndex === deviceIndex)
            );
        }
    } else {
        // Zone not explicitly selected - might be selected because device is selected
        // Deselect parent device if selected, then select this zone
        if (isDeviceSelected(deviceIndex)) {
            selectedItems = selectedItems.filter(item => 
                !(item.type === 'device' && item.deviceIndex === deviceIndex)
            );
        }
        selectedItems.push({ type: 'zone', deviceIndex, zoneIndex });
    }
    displayDevices();
    updateSelectionStatus();
}

function updateSelectionStatus() {
    const count = selectedItems.length;
    if (count === 0) {
        updateSelectionText('No devices or zones selected');
        // Reset sliders to default
        document.getElementById('brightnessSlider').value = 100;
        document.getElementById('saturationSlider').value = 100;
        document.getElementById('brightnessValue').textContent = '100%';
        document.getElementById('saturationValue').textContent = '100%';
    } else {
        // Count unique devices (either selected directly or have zones selected)
        const deviceIndices = new Set();
        selectedItems.forEach(item => {
            deviceIndices.add(item.deviceIndex);
        });
        const deviceCount = deviceIndices.size;
        
        // Count total zones and LEDs (excluding disabled zones)
        let zoneCount = 0;
        let ledCount = 0;
        
        selectedItems.forEach(item => {
            if (item.type === 'device') {
                // Add all enabled zones in this device
                const device = devices[item.deviceIndex];
                if (device && device.zones) {
                    device.zones.forEach(zone => {
                        if (!zone.excluded) {
                            zoneCount += 1;
                            ledCount += zone.leds || 0;
                        }
                    });
                }
            } else if (item.type === 'zone') {
                // Add individual zone if not disabled
                const device = devices[item.deviceIndex];
                const zone = device?.zones[item.zoneIndex];
                if (zone && !zone.excluded) {
                    zoneCount += 1;
                    ledCount += zone.leds || 0;
                }
            }
        });
        
        updateSelectionText(`✓ ${deviceCount} Devices | ${zoneCount} Zones | ${ledCount} LEDs`);
        
        // If only one zone is selected (and no whole devices), load its brightness/saturation
        const onlyZones = selectedItems.filter(i => i.type === 'zone');
        const onlyDevices = selectedItems.filter(i => i.type === 'device');
        
        if (onlyZones.length === 1 && onlyDevices.length === 0) {
            const zoneItem = onlyZones[0];
            const device = devices[zoneItem.deviceIndex];
            const zone = device.zones[zoneItem.zoneIndex];
            
            if (zone) {
                document.getElementById('brightnessSlider').value = zone.brightness || 100;
                document.getElementById('saturationSlider').value = zone.saturation || 100;
                document.getElementById('brightnessValue').textContent = (zone.brightness || 100) + '%';
                document.getElementById('saturationValue').textContent = (zone.saturation || 100) + '%';
            }
        }
        // If only one device is selected, load its first zone's brightness/saturation
        else if (deviceCount === 1 && zoneCount === 0) {
            const deviceItem = selectedItems.find(i => i.type === 'device');
            const device = devices[deviceItem.deviceIndex];
            
            if (device && device.zones.length > 0) {
                const firstZone = device.zones[0];
                document.getElementById('brightnessSlider').value = firstZone.brightness || 100;
                document.getElementById('saturationSlider').value = firstZone.saturation || 100;
                document.getElementById('brightnessValue').textContent = (firstZone.brightness || 100) + '%';
                document.getElementById('saturationValue').textContent = (firstZone.saturation || 100) + '%';
            }
        }
    }
}

// Toggle disabled devices section
function toggleDisabledDevices() {
    const list = document.getElementById('disabledDevicesList');
    const icon = document.getElementById('disabledCollapseIcon');
    
    if (list.style.display === 'none') {
        list.style.display = 'block';
        icon.textContent = '▼';
    } else {
        list.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Toggle disabled zones section for a specific device
function toggleDisabledZones(deviceIndex) {
    const list = document.getElementById(`disabledZonesList-${deviceIndex}`);
    const icon = document.getElementById(`disabledZonesIcon-${deviceIndex}`);
    
    if (list.style.display === 'none') {
        list.style.display = 'block';
        icon.textContent = '▼';
    } else {
        list.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Toggle device enabled/disabled
async function toggleDevice(deviceName, deviceIndex) {
    try {
        const response = await fetch('/api/device/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_name: deviceName })
        });
        
        const data = await response.json();
        if (data.success) {
            const status = data.excluded ? 'disabled' : 'enabled';
            updateStatus(`✓ ${deviceName} ${status}`, 'success');
            // Reload devices to update UI
            await loadDevices();
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to toggle device', 'error');
        console.error('Error:', error);
    }
}

// Flash zone to identify it visually
async function flashZone(deviceIndex, zoneIndex) {
    try {
        updateStatus('⚡ Flashing zone...', 'info');
        const response = await fetch('/api/zone/flash', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                device_index: deviceIndex, 
                zone_index: zoneIndex,
                flashes: 5  // Flash 5 times (white/black alternating)
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus('✓ Zone flashed!', 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to flash zone', 'error');
        console.error('Error:', error);
    }
}

// Toggle zone exclusion (hide/show)
async function toggleZoneExclusion(deviceName, deviceIndex, zoneIndex) {
    try {
        const response = await fetch('/api/zone/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device: deviceIndex, zone: zoneIndex })
        });
        
        const data = await response.json();
        if (data.success) {
            const status = data.excluded ? 'disabled' : 'enabled';
            updateStatus(`✓ Zone ${status}`, 'success');
            // Remove from selection if it was selected
            if (data.excluded) {
                selectedItems = selectedItems.filter(item => 
                    !(item.type === 'zone' && item.deviceIndex === deviceIndex && item.zoneIndex === zoneIndex)
                );
            }
            // Reload devices to update UI
            await loadDevices();
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to toggle zone', 'error');
        console.error('Error:', error);
    }
}

// Reset all devices to Direct mode and reapply colors
async function resetDeviceModes() {
    if (!confirm('Force all devices back to Direct mode and reapply colors?\n\nUse this if devices are stuck in hardware modes (like rainbow).')) {
        return;
    }
    
    updateStatus('⏳ Resetting devices...', 'info');
    
    try {
        const response = await fetch('/api/reset-modes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus('✓ ' + data.message, 'success');
            await loadDevices(); // Refresh UI
        } else {
            updateStatus('✗ Failed to reset: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to reset devices', 'error');
        console.error('Error:', error);
    }
}

// Set zone color from mini color picker
async function setZoneColorFromPicker(deviceIndex, zoneIndex, hexColor) {
    try {
        // Convert hex to RGB
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        
        const response = await fetch('/api/zone/color', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device: deviceIndex,
                zone: zoneIndex,
                r: r,
                g: g,
                b: b
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Zone color updated to RGB(${r}, ${g}, ${b})`, 'success');
            await loadDevices(); // Refresh UI
        } else {
            updateStatus('✗ Failed to set zone color: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to set zone color', 'error');
        console.error('Error:', error);
    }
}

// Update zone slider value display
function updateZoneSliderValue(deviceIndex, zoneIndex, type, value) {
    const elementId = `zone-${type}-${deviceIndex}-${zoneIndex}`;
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value + '%';
    }
}

// Apply brightness/saturation to a specific zone
async function applyZoneBrightnessSaturation(deviceIndex, zoneIndex) {
    try {
        const brightnessElement = document.getElementById(`zone-brightness-${deviceIndex}-${zoneIndex}`);
        const saturationElement = document.getElementById(`zone-saturation-${deviceIndex}-${zoneIndex}`);
        
        const brightness = parseInt(brightnessElement.textContent);
        const saturation = parseInt(saturationElement.textContent);
        
        const response = await fetch('/api/zone/brightness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device: deviceIndex,
                zone: zoneIndex,
                brightness: brightness,
                saturation: saturation
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Zone brightness: ${brightness}%, saturation: ${saturation}%`, 'success');
            await loadDevices(); // Refresh UI
        } else {
            updateStatus('✗ Failed to update zone: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to update zone brightness/saturation', 'error');
        console.error('Error:', error);
    }
}

// Setup color control listeners
function setupColorControls() {
    const colorPicker = document.getElementById('colorPicker');
    const rSlider = document.getElementById('rSlider');
    const gSlider = document.getElementById('gSlider');
    const bSlider = document.getElementById('bSlider');
    const colorDisplay = document.getElementById('colorDisplay');
    
    // Color picker change
    colorPicker.addEventListener('input', (e) => {
        const hex = e.target.value;
        const rgb = hexToRgb(hex);
        updateRGBSliders(rgb.r, rgb.g, rgb.b);
    });
    
    // RGB sliders
    [rSlider, gSlider, bSlider].forEach(slider => {
        slider.addEventListener('input', () => {
            const r = parseInt(rSlider.value);
            const g = parseInt(gSlider.value);
            const b = parseInt(bSlider.value);
            
            document.getElementById('rValue').textContent = r;
            document.getElementById('gValue').textContent = g;
            document.getElementById('bValue').textContent = b;
            
            const hex = rgbToHex(r, g, b);
            colorPicker.value = hex;
            colorDisplay.style.background = `rgb(${r}, ${g}, ${b})`;
        });
    });
}

// Setup effect control listeners
function setupEffectControls() {
    const brightnessSlider = document.getElementById('brightnessSlider');
    const saturationSlider = document.getElementById('saturationSlider');
    
    if (brightnessSlider) {
        brightnessSlider.addEventListener('input', (e) => {
            document.getElementById('brightnessValue').textContent = e.target.value + '%';
        });
        brightnessSlider.addEventListener('change', () => {
            applyBrightnessSaturation();
        });
    }
    
    if (saturationSlider) {
        saturationSlider.addEventListener('input', (e) => {
            document.getElementById('saturationValue').textContent = e.target.value + '%';
        });
        saturationSlider.addEventListener('change', () => {
            applyBrightnessSaturation();
        });
    }
}

// Apply brightness/saturation to selected zones
async function applyBrightnessSaturation() {
    if (selectedItems.length === 0) {
        return; // Silently return if nothing selected
    }
    
    const brightness = parseInt(document.getElementById('brightnessSlider').value);
    const saturation = parseInt(document.getElementById('saturationSlider').value);
    
    for (const item of selectedItems) {
        if (item.type === 'zone') {
            // Apply to single zone
            try {
                const response = await fetch('/api/zone/brightness', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        device: item.deviceIndex,
                        zone: item.zoneIndex,
                        brightness: brightness,
                        saturation: saturation
                    })
                });
                
                const data = await response.json();
                if (!data.success) {
                    updateStatus(`✗ Failed to set brightness/saturation: ${data.error}`, 'error');
                }
            } catch (error) {
                updateStatus('✗ Failed to set brightness/saturation', 'error');
                console.error('Error:', error);
            }
        } else if (item.type === 'device') {
            // Apply to all zones in the device
            const device = devices[item.deviceIndex];
            for (let zoneIndex = 0; zoneIndex < device.zones.length; zoneIndex++) {
                try {
                    const response = await fetch('/api/zone/brightness', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            device: item.deviceIndex,
                            zone: zoneIndex,
                            brightness: brightness,
                            saturation: saturation
                        })
                    });
                    
                    const data = await response.json();
                    if (!data.success) {
                        updateStatus(`✗ Failed to set brightness/saturation: ${data.error}`, 'error');
                    }
                } catch (error) {
                    updateStatus('✗ Failed to set brightness/saturation', 'error');
                    console.error('Error:', error);
                }
            }
        }
    }
    
    updateStatus(`✓ Brightness: ${brightness}%, Saturation: ${saturation}%`, 'success');
}

// Apply color to selected items
async function applyColor() {
    if (selectedItems.length === 0) {
        updateStatus('⚠ Please select at least one device or zone', 'error');
        return;
    }
    
    const colorPicker = document.getElementById('colorPicker');
    const hex = colorPicker.value;
    const rgb = hexToRgb(hex);
    
    // Save to recent colors
    saveRecentColor(rgb.r, rgb.g, rgb.b);
    
    try {
        // Group items by device to avoid conflicts
        const deviceIndices = new Set(selectedItems.filter(i => i.type === 'device').map(i => i.deviceIndex));
        const zonesToUpdate = selectedItems.filter(i => 
            i.type === 'zone' && !deviceIndices.has(i.deviceIndex)
        );
        
        // Apply to devices (entire device at once)
        for (const deviceIndex of deviceIndices) {
            const response = await fetch('/api/color', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ r: rgb.r, g: rgb.g, b: rgb.b, device: deviceIndex })
            });
            const data = await response.json();
            if (!data.success) {
                updateStatus(`✗ Error setting color for device ${deviceIndex}`, 'error');
                return;
            }
        }
        
        // Apply to individual zones (only if parent device not selected)
        for (const item of zonesToUpdate) {
            const response = await fetch('/api/zone/color', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    device: item.deviceIndex, 
                    zone: item.zoneIndex, 
                    r: rgb.r, 
                    g: rgb.g, 
                    b: rgb.b 
                })
            });
            const data = await response.json();
            if (!data.success) {
                updateStatus(`✗ Error setting color for zone ${item.zoneIndex}`, 'error');
                return;
            }
        }
        
        updateStatus(`✓ Color applied to ${selectedItems.length} item(s)`, 'success');
    } catch (error) {
        updateStatus('✗ Failed to apply color', 'error');
        console.error('Error:', error);
    }
}

// Apply preset color to selected items
async function applyPresetColor(r, g, b) {
    if (selectedItems.length === 0) {
        updateStatus('⚠ Please select at least one device or zone', 'error');
        return;
    }
    
    const hex = rgbToHex(r, g, b);
    document.getElementById('colorPicker').value = hex;
    await applyColor();
}

// Show resize dialog
function showResizeDialog(deviceIndex, zoneIndex, min, max, current) {
    const newSize = prompt(`Resize zone (${min}-${max} LEDs):`, current);
    if (newSize !== null) {
        const size = parseInt(newSize);
        if (size >= min && size <= max) {
            resizeZone(deviceIndex, zoneIndex, size);
        } else {
            updateStatus(`✗ Size must be between ${min} and ${max}`, 'error');
        }
    }
}

// Set color (old function - kept for compatibility)
async function setColor() {
    const r = parseInt(document.getElementById('rSlider').value);
    const g = parseInt(document.getElementById('gSlider').value);
    const b = parseInt(document.getElementById('bSlider').value);
    const device = getSelectedDevice();
    
    try {
        const response = await fetch('/api/color', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ r, g, b, device })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Color set to RGB(${r}, ${g}, ${b})`, 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to set color', 'error');
        console.error('Error:', error);
    }
}

// Apply preset color
function applyPreset(r, g, b) {
    updateRGBSliders(r, g, b);
    setColor();
}

// Resize zone
async function resizeZone(deviceIndex, zoneIndex, newSize) {
    // If newSize not provided, try to get from input (backward compatibility)
    if (newSize === undefined) {
        const input = document.getElementById(`zone-${deviceIndex}-${zoneIndex}`);
        if (input) {
            newSize = parseInt(input.value);
        } else {
            updateStatus('✗ Invalid resize parameters', 'error');
            return;
        }
    }
    
    try {
        const response = await fetch('/api/zone/resize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device: deviceIndex, zone: zoneIndex, size: newSize })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Zone resized to ${data.new_size} LEDs`, 'success');
            // Reload devices to show updated info
            setTimeout(loadDevices, 500);
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to resize zone', 'error');
        console.error('Error:', error);
    }
}

// Set zone color
async function setZoneColor(deviceIndex, zoneIndex) {
    const colorPicker = document.getElementById(`zone-color-${deviceIndex}-${zoneIndex}`);
    const hex = colorPicker.value;
    const rgb = hexToRgb(hex);
    
    try {
        const response = await fetch('/api/zone/color', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                device: deviceIndex, 
                zone: zoneIndex, 
                r: rgb.r, 
                g: rgb.g, 
                b: rgb.b 
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Zone color updated to RGB(${rgb.r}, ${rgb.g}, ${rgb.b})`, 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to set zone color', 'error');
        console.error('Error:', error);
    }
}

// Edit zone name
async function editZoneName(deviceIndex, zoneIndex, originalName, currentFriendlyName) {
    const friendlyName = prompt(
        `Enter a friendly name for zone:\n"${originalName}"\n\n` +
        `Leave blank to remove custom name and use original.`,
        currentFriendlyName
    );
    
    // User canceled
    if (friendlyName === null) return;
    
    try {
        const response = await fetch('/api/zone/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device: deviceIndex,
                zone: zoneIndex,
                name: friendlyName.trim()
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Zone renamed${friendlyName.trim() ? ' to "' + friendlyName.trim() + '"' : ''}`, 'success');
            await loadDevices(); // Refresh the UI
        } else {
            updateStatus('✗ Failed to rename zone: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to rename zone', 'error');
        console.error('Error:', error);
    }
}

// Set zone effect
async function setZoneEffect(deviceIndex, zoneIndex, effectType) {
    try {
        // Get effect parameters based on type
        let effectParams = null;
        
        if (effectType === 'breathing') {
            // Use current color for breathing effect
            const device = devices[deviceIndex];
            const zone = device.zones[zoneIndex];
            // Try to get stored color or use default
            effectParams = {
                color: { r: 255, g: 0, b: 0 },  // Default red
                speed: 1.0
            };
        } else if (effectType === 'rainbow' || effectType === 'wave') {
            effectParams = {
                speed: 1.0
            };
        } else if (effectType === 'cycle') {
            effectParams = {
                colors: [
                    { r: 255, g: 0, b: 0 },    // Red
                    { r: 0, g: 255, b: 0 },    // Green
                    { r: 0, g: 0, b: 255 }     // Blue
                ],
                speed: 1.0
            };
        }
        
        const response = await fetch('/api/zone/effect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device: deviceIndex,
                zone: zoneIndex,
                effect_type: effectType,
                effect_params: effectParams
            })
        });
        
        const data = await response.json();
        if (data.success) {
            const effectNames = {
                'static': 'Static',
                'rainbow': 'Rainbow 🌈',
                'breathing': 'Breathing 💨',
                'wave': 'Wave 🌊',
                'cycle': 'Cycle 🔄'
            };
            updateStatus(`✓ Effect set to ${effectNames[effectType]}`, 'success');
        } else {
            updateStatus('✗ Failed to set effect: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to set effect', 'error');
        console.error('Error:', error);
    }
}

// Set effect for all zones in a device
async function setDeviceEffect(deviceIndex, effectType) {
    if (!effectType) return; // User selected the placeholder option
    
    try {
        const device = devices[deviceIndex];
        updateStatus(`⏳ Setting ${effectType} effect for all zones in ${device.name}...`, 'info');
        
        // Get effect parameters based on type
        let effectParams = null;
        
        if (effectType === 'breathing') {
            effectParams = {
                color: { r: 255, g: 0, b: 0 },  // Default red
                speed: 1.0
            };
        } else if (effectType === 'rainbow' || effectType === 'wave') {
            effectParams = {
                speed: 1.0
            };
        } else if (effectType === 'cycle') {
            effectParams = {
                colors: [
                    { r: 255, g: 0, b: 0 },    // Red
                    { r: 0, g: 255, b: 0 },    // Green
                    { r: 0, g: 0, b: 255 }     // Blue
                ],
                speed: 1.0
            };
        }
        
        // Apply effect to all zones
        for (let zoneIndex = 0; zoneIndex < device.zones.length; zoneIndex++) {
            const response = await fetch('/api/zone/effect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device: deviceIndex,
                    zone: zoneIndex,
                    effect_type: effectType,
                    effect_params: effectParams
                })
            });
            
            const data = await response.json();
            if (!data.success) {
                updateStatus(`✗ Failed to set effect for zone ${zoneIndex}: ${data.error}`, 'error');
                return;
            }
        }
        
        const effectNames = {
            'static': 'Static',
            'rainbow': 'Rainbow 🌈',
            'breathing': 'Breathing 💨',
            'wave': 'Wave 🌊',
            'cycle': 'Cycle 🔄'
        };
        updateStatus(`✓ Set all zones to ${effectNames[effectType]}`, 'success');
        
        // Reload devices to update UI
        await loadDevices();
    } catch (error) {
        updateStatus('✗ Failed to set device effect', 'error');
        console.error('Error:', error);
    }
}

// Helper functions
function getSelectedDevice() {
    const selected = document.querySelector('input[name="targetDevice"]:checked').value;
    return selected === 'all' ? null : parseInt(selected);
}

function updateRGBSliders(r, g, b) {
    document.getElementById('rSlider').value = r;
    document.getElementById('gSlider').value = g;
    document.getElementById('bSlider').value = b;
    document.getElementById('rValue').textContent = r;
    document.getElementById('gValue').textContent = g;
    document.getElementById('bValue').textContent = b;
    document.getElementById('colorDisplay').style.background = `rgb(${r}, ${g}, ${b})`;
    document.getElementById('colorPicker').value = rgbToHex(r, g, b);
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
}

function rgbToHex(r, g, b) {
    return "#" + [r, g, b].map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
    }).join('');
}

function updateStatus(message, type = '') {
    const statusBar = document.getElementById('statusBar');
    const statusText = document.getElementById('statusText');
    
    statusText.textContent = message;
    statusBar.className = 'status-bar ' + type;
}

function updateSelectionText(message) {
    const selectionText = document.getElementById('selectionText');
    if (selectionText) {
        selectionText.textContent = message;
    }
}

// Recent Colors Management
function loadRecentColors() {
    fetch('/api/colors/recent')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                recentColors = data.colors;
                updateRecentColorsDisplay();
            }
        })
        .catch(error => {
            console.error('Error loading recent colors:', error);
            recentColors = [];
        });
}

async function saveRecentColor(r, g, b) {
    try {
        const response = await fetch('/api/colors/recent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ r, g, b })
        });
        
        const data = await response.json();
        if (data.success) {
            // Reload recent colors to get updated list
            loadRecentColors();
        }
    } catch (error) {
        console.error('Error saving recent color:', error);
    }
}

function updateRecentColorsDisplay() {
    const section = document.getElementById('recentColorsSection');
    const grid = document.getElementById('recentColorsGrid');
    
    if (recentColors.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'flex';
    
    // Generate recent color buttons
    grid.innerHTML = recentColors.map(color => {
        const hex = rgbToHex(color.r, color.g, color.b);
        return `<button class="color-preset" 
                        style="background: ${hex}" 
                        onclick="applyPresetColor(${color.r},${color.g},${color.b})" 
                        title="RGB(${color.r}, ${color.g}, ${color.b})"></button>`;
    }).join('');
}
