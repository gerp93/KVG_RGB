// Global state
let devices = [];
let currentEffect = null;
let selectedItems = []; // Array of {type: 'device'|'zone', deviceIndex, zoneIndex (optional)}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
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
                <button class="device-toggle-mini" 
                        onclick="event.stopPropagation(); toggleDevice('${device.name.replace(/'/g, "\\'")}', ${device.index})"
                        title="Disable this device">
                    🟢
                </button>
            </div>
            
            ${device.zones.length > 0 ? `
                <!-- Zones List -->
                <div class="zones-container">
                    ${device.zones.filter(z => !z.excluded).map((zone) => {
                        const originalZoneIndex = device.zones.indexOf(zone);
                        return `
                        <div class="zone-item-selectable ${isZoneSelected(device.index, originalZoneIndex) ? 'selected' : ''}"
                             onclick="toggleZoneSelection(${device.index}, ${originalZoneIndex})"
                             data-device="${device.index}"
                             data-zone="${originalZoneIndex}">
                            <div class="selection-indicator">
                                <span class="checkbox">${isZoneSelected(device.index, originalZoneIndex) ? '☑' : '☐'}</span>
                            </div>
                            <div class="zone-info-compact">
                                <div class="zone-name-text">${zone.name}</div>
                                <div class="zone-led-count">${zone.leds} LEDs</div>
                            </div>
                            <div class="zone-actions">
                                ${zone.leds_min !== null && zone.leds_max !== null && zone.leds_min !== zone.leds_max ? `
                                    <button class="btn-mini" 
                                            onclick="event.stopPropagation(); showResizeDialog(${device.index}, ${originalZoneIndex}, ${zone.leds_min}, ${zone.leds_max}, ${zone.leds})"
                                            title="Resize zone">
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
    
    // If device is selected, deselect it first
    if (isDeviceSelected(deviceIndex)) {
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'device' && item.deviceIndex === deviceIndex)
        );
    }
    
    if (isZoneSelected(deviceIndex, zoneIndex)) {
        // Deselect zone
        selectedItems = selectedItems.filter(item => 
            !(item.type === 'zone' && item.deviceIndex === deviceIndex && item.zoneIndex === zoneIndex)
        );
    } else {
        // Select zone
        selectedItems.push({ type: 'zone', deviceIndex, zoneIndex });
    }
    displayDevices();
    updateSelectionStatus();
}

function updateSelectionStatus() {
    const count = selectedItems.length;
    if (count === 0) {
        updateStatus('No devices or zones selected', 'info');
    } else {
        const deviceCount = selectedItems.filter(i => i.type === 'device').length;
        const zoneCount = selectedItems.filter(i => i.type === 'zone').length;
        updateStatus(`Selected: ${deviceCount} device(s), ${zoneCount} zone(s)`, 'success');
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
    const rainbowSpeed = document.getElementById('rainbowSpeed');
    const breatheSpeed = document.getElementById('breatheSpeed');
    
    if (rainbowSpeed) {
        rainbowSpeed.addEventListener('input', (e) => {
            document.getElementById('rainbowSpeedValue').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
        });
    }
    
    if (breatheSpeed) {
        breatheSpeed.addEventListener('input', (e) => {
            document.getElementById('breatheSpeedValue').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
        });
    }
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

// Start rainbow effect
async function startRainbow() {
    const duration = parseInt(document.getElementById('rainbowDuration').value);
    const speed = parseFloat(document.getElementById('rainbowSpeed').value);
    const device = getSelectedDevice();
    
    try {
        const response = await fetch('/api/effect/rainbow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ duration, speed, device })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Rainbow effect started (${duration}s)`, 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to start rainbow effect', 'error');
        console.error('Error:', error);
    }
}

// Start breathing effect
async function startBreathe() {
    const duration = parseInt(document.getElementById('breatheDuration').value);
    const speed = parseFloat(document.getElementById('breatheSpeed').value);
    const color = document.getElementById('breatheColor').value;
    const rgb = hexToRgb(color);
    const device = getSelectedDevice();
    
    try {
        const response = await fetch('/api/effect/breathe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ r: rgb.r, g: rgb.g, b: rgb.b, duration, speed, device })
        });
        
        const data = await response.json();
        if (data.success) {
            updateStatus(`✓ Breathing effect started (${duration}s)`, 'success');
        } else {
            updateStatus('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('✗ Failed to start breathing effect', 'error');
        console.error('Error:', error);
    }
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
