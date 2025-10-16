// Global state
let devices = [];
let currentEffect = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDevices();
    setupColorControls();
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

// Display devices in the UI
function displayDevices() {
    const deviceList = document.getElementById('deviceList');
    const deviceSelector = document.querySelector('.device-selector');
    
    if (devices.length === 0) {
        deviceList.innerHTML = '<p class="info">No RGB devices found</p>';
        return;
    }
    
    // Display device cards with toggle buttons
    deviceList.innerHTML = devices.map(device => `
        <div class="device-item ${device.excluded ? 'excluded' : ''}" id="device-${device.index}">
            <div class="device-header">
                <div class="device-name">${device.name}</div>
                <button class="device-toggle" 
                        onclick="toggleDevice('${device.name}', ${device.index})"
                        title="${device.excluded ? 'Enable this device' : 'Disable this device'}">
                    ${device.excluded ? '🔴' : '🟢'}
                </button>
            </div>
            <div class="device-info">
                💡 ${device.leds} LEDs | 📦 ${device.zones.length} Zones
            </div>
        </div>
    `).join('');
    
    // Add device selector radio buttons (only for active devices)
    const activeDevices = devices.filter(d => !d.excluded);
    const deviceRadios = activeDevices.map(device => `
        <label>
            <input type="radio" name="targetDevice" value="${device.index}">
            ${device.name}
        </label>
    `).join('');
    
    deviceSelector.innerHTML = `
        <label>
            <input type="radio" name="targetDevice" value="all" checked>
            All Active Devices
        </label>
        ${deviceRadios}
    `;
    
    // Display zones
    displayZones();
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

// Display zones for management
function displayZones() {
    const zoneList = document.getElementById('zoneList');
    
    const devicesWithZones = devices.filter(d => d.zones.length > 0);
    
    if (devicesWithZones.length === 0) {
        zoneList.innerHTML = '<p class="info">No zones found on any device</p>';
        return;
    }
    
    zoneList.innerHTML = devicesWithZones.map(device => `
        <div class="zone-device">
            <div class="zone-device-name">${device.name}</div>
            <div class="zones-grid">
                ${device.zones.map(zone => `
                    <div class="zone-item">
                        <div class="zone-header">
                            <span class="zone-name">${zone.name}</span>
                            <span class="zone-size">${zone.leds} LEDs</span>
                        </div>
                        ${zone.leds_min !== null && zone.leds_max !== null ? `
                            <div class="zone-info">
                                Range: ${zone.leds_min}-${zone.leds_max} LEDs
                            </div>
                            ${zone.leds_min !== zone.leds_max ? `
                                <div class="zone-resize">
                                    <input type="number" 
                                           id="zone-${device.index}-${zone.index}" 
                                           min="${zone.leds_min}" 
                                           max="${zone.leds_max}" 
                                           value="${zone.leds}">
                                    <button class="btn btn-primary" 
                                            onclick="resizeZone(${device.index}, ${zone.index})">
                                        Resize
                                    </button>
                                </div>
                            ` : '<p class="zone-info">Fixed size zone</p>'}
                        ` : '<p class="zone-info">Zone info not available</p>'}
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
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
    
    rainbowSpeed.addEventListener('input', (e) => {
        document.getElementById('rainbowSpeedValue').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
    });
    
    breatheSpeed.addEventListener('input', (e) => {
        document.getElementById('breatheSpeedValue').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
    });
}

// Set color
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
async function resizeZone(deviceIndex, zoneIndex) {
    const input = document.getElementById(`zone-${deviceIndex}-${zoneIndex}`);
    const newSize = parseInt(input.value);
    
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
