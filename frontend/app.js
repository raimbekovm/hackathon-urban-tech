// Initialize map centered on Bishkek
const map = L.map('map').setView([42.8746, 74.5698], 12);

// Define tile layers
const tileLayers = {
    streets: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap, © CartoDB',
        maxZoom: 19
    }),
    dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap, © CartoDB',
        maxZoom: 19
    }),
    satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri',
        maxZoom: 19
    })
};

// Add default layer (streets)
let currentTileLayer = tileLayers.streets.addTo(map);

// Data storage
let defectsData = [];
let worstRoadsData = [];
let statsData = {};
let heatmapLayer = null;
let markersLayer = L.layerGroup().addTo(map);
let districtsLayer = L.layerGroup();

// Defect type colors
const DEFECT_COLORS = {
    'pothole': '#ef4444',
    'longitudinal_crack': '#f59e0b',
    'transverse_crack': '#10b981',
    'alligator_crack': '#8b5cf6',
    'other_damage': '#6b7280'
};

const DEFECT_NAMES = {
    'pothole': 'Яма',
    'longitudinal_crack': 'Продольная трещина',
    'transverse_crack': 'Поперечная трещина',
    'alligator_crack': 'Сетка трещин',
    'other_damage': 'Другие дефекты'
};

// Load data
async function loadData() {
    try {
        console.log('Loading data...');

        // Add timestamp to avoid cache
        const timestamp = new Date().getTime();

        // Load defects
        const defectsResponse = await fetch(`../ml/output/defects.csv?t=${timestamp}`);
        const defectsText = await defectsResponse.text();
        defectsData = parseCSV(defectsText);
        console.log('Defects loaded:', defectsData.length, defectsData[0]);

        // Load worst roads
        const worstRoadsResponse = await fetch(`../ml/output/worst_roads.json?t=${timestamp}`);
        const worstRoadsJson = await worstRoadsResponse.json();
        worstRoadsData = worstRoadsJson.worst_roads || worstRoadsJson;
        console.log('Worst roads loaded:', worstRoadsData.length, worstRoadsData[0]);

        // Load stats
        const statsResponse = await fetch(`../ml/output/stats.json?t=${timestamp}`);
        statsData = await statsResponse.json();
        console.log('Stats loaded:', statsData);

        // Load heatmap
        const heatmapResponse = await fetch(`../ml/output/heatmap.json?t=${timestamp}`);
        const heatmapJson = await heatmapResponse.json();
        const heatmapData = heatmapJson.heatmap_data || heatmapJson;
        console.log('Heatmap loaded:', heatmapData.length);

        // Initialize visualizations
        console.log('Initializing visualizations...');
        updateStats();
        createDefectChart();
        createWorstRoadsList();
        createMarkers();
        createHeatmap(heatmapData);

        // Add legend
        addLegend();

        console.log('All data loaded successfully!');

    } catch (error) {
        console.error('Error loading data:', error);
        alert('Ошибка загрузки данных: ' + error.message);
    }
}

// Parse CSV
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',');

    return lines.slice(1).map(line => {
        const values = line.split(',');
        const obj = {};
        headers.forEach((header, i) => {
            obj[header.trim()] = values[i]?.trim();
        });
        return obj;
    });
}

// Update statistics
function updateStats() {
    console.log('updateStats called with:', statsData);
    const stats = statsData.total_stats || statsData;
    console.log('Using stats:', stats);

    const totalDefects = stats.total_defects || 0;
    const criticalDefects = stats.critical_defects || 0;
    const quality = Math.max(0, 100 - (totalDefects / 2));
    const costMillion = ((stats.total_repair_cost || 0) / 1000000).toFixed(1);

    console.log('Setting values:', { totalDefects, criticalDefects, quality, costMillion });

    document.getElementById('totalDefects').textContent = totalDefects;
    document.getElementById('criticalDefects').textContent = criticalDefects;
    document.getElementById('roadQuality').textContent = Math.round(quality);
    document.getElementById('repairCost').textContent = `${costMillion}M KGS`;

    console.log('Stats updated successfully');
}

// Create defect type chart
function createDefectChart() {
    const ctx = document.getElementById('defectChart');

    const defectCounts = {};
    defectsData.forEach(d => {
        const type = d.defect_type || 'unknown';
        defectCounts[type] = (defectCounts[type] || 0) + 1;
    });

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(defectCounts).map(k => DEFECT_NAMES[k] || k),
            datasets: [{
                data: Object.values(defectCounts),
                backgroundColor: Object.keys(defectCounts).map(k => DEFECT_COLORS[k] || '#6b7280'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'white',
                        font: {
                            size: 11
                        },
                        padding: 12
                    }
                }
            }
        }
    });
}

// Create worst roads list
function createWorstRoadsList() {
    const container = document.getElementById('worstRoads');
    container.innerHTML = '';

    worstRoadsData.slice(0, 10).forEach((road, index) => {
        const li = document.createElement('li');
        li.className = 'road-item';

        const priority = road.priority_score >= 8 ? 'critical' :
                        road.priority_score >= 6 ? 'high' : 'medium';

        li.innerHTML = `
            <div class="road-name">${road.rank || index + 1}. ${road.street_name}</div>
            <div class="road-stats">
                <span>Дефектов: ${road.defect_count || road.total_defects || 0}</span>
                <span>Серьезность: ${road.avg_severity.toFixed(1)}/10</span>
            </div>
            <span class="priority-badge priority-${priority}">
                Приоритет: ${road.priority_score.toFixed(1)}/10
            </span>
        `;

        li.addEventListener('click', () => {
            // Find first defect on this road and zoom to it
            const defect = defectsData.find(d => d.street_name === road.street_name);
            if (defect) {
                map.setView([parseFloat(defect.lat), parseFloat(defect.lon)], 16);
            }
        });

        container.appendChild(li);
    });
}

// Create markers for defects
function createMarkers() {
    markersLayer.clearLayers();

    defectsData.forEach(defect => {
        const lat = parseFloat(defect.lat);
        const lon = parseFloat(defect.lon);

        if (isNaN(lat) || isNaN(lon)) return;

        const color = DEFECT_COLORS[defect.defect_type] || '#6b7280';
        const severity = parseFloat(defect.severity) || 0;

        const marker = L.circleMarker([lat, lon], {
            radius: 6 + (severity / 10) * 4,
            fillColor: color,
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        const repairCost = Math.round(severity * 3500 + Math.random() * 10000);

        const popupContent = `
            <div class="defect-popup">
                <h4>${DEFECT_NAMES[defect.defect_type] || defect.defect_type}</h4>
                <div class="defect-details">
                    <div><strong>Улица:</strong> ${defect.street_name || 'Unknown Street'}</div>
                    <div><strong>Район:</strong> ${defect.district || 'Unknown'}</div>
                    <div><strong>Серьезность:</strong> ${severity.toFixed(1)}/10</div>
                    <div><strong>Уверенность:</strong> ${(parseFloat(defect.confidence) * 100).toFixed(0)}%</div>
                    <div><strong>Фото:</strong> ${defect.image_path}</div>
                    <div><strong>Стоимость:</strong> ~${repairCost.toLocaleString()} KGS</div>
                </div>
                <div class="severity-bar">
                    <div class="severity-fill" style="width: ${severity * 10}%"></div>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent);
        marker.addTo(markersLayer);
    });
}

// Create heatmap
function createHeatmap(heatmapData) {
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
    }

    // heatmapData is array of [lat, lon, intensity]
    const points = heatmapData.map(point => {
        if (Array.isArray(point)) {
            return point; // Already in correct format
        } else {
            return [point.lat, point.lon, point.intensity];
        }
    });

    heatmapLayer = L.heatLayer(points, {
        radius: 25,
        blur: 35,
        maxZoom: 17,
        max: 1.0,
        gradient: {
            0.0: '#10b981',
            0.3: '#facc15',
            0.6: '#fb923c',
            1.0: '#ef4444'
        }
    });
}

// Add legend
function addLegend() {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = '<h4>Типы дефектов</h4>';

        Object.entries(DEFECT_NAMES).forEach(([key, name]) => {
            div.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background: ${DEFECT_COLORS[key]}"></div>
                    <span>${name}</span>
                </div>
            `;
        });

        return div;
    };

    legend.addTo(map);
}

// Critical defects layer
let criticalLayer = L.layerGroup();

function showCriticalDefects() {
    criticalLayer.clearLayers();

    // Filter critical defects (severity >= 7)
    const criticalDefects = defectsData.filter(d => parseFloat(d.severity) >= 7);

    console.log(`Showing ${criticalDefects.length} critical defects`);

    criticalDefects.forEach(defect => {
        const lat = parseFloat(defect.lat);
        const lon = parseFloat(defect.lon);

        if (isNaN(lat) || isNaN(lon)) return;

        const severity = parseFloat(defect.severity);

        // Pulsating marker for critical defects
        const baseRadius = 8 + (severity / 10) * 6;
        const marker = L.circleMarker([lat, lon], {
            radius: baseRadius,
            fillColor: '#ef4444',
            color: '#fef2f2',
            weight: 3,
            opacity: 1,
            fillOpacity: 0.9
        });

        // Add smooth pulse effect
        let growing = true;
        let currentRadius = baseRadius;
        setInterval(() => {
            if (growing) {
                currentRadius += 0.5;
                if (currentRadius >= baseRadius + 3) growing = false;
            } else {
                currentRadius -= 0.5;
                if (currentRadius <= baseRadius) growing = true;
            }
            marker.setRadius(currentRadius);
        }, 50);

        const repairCost = Math.round(severity * 3500 + Math.random() * 10000);

        const popupContent = `
            <div class="defect-popup">
                <h4>⚠️ ${DEFECT_NAMES[defect.defect_type] || defect.defect_type}</h4>
                <div class="defect-details">
                    <div><strong>Улица:</strong> ${defect.street_name || 'Unknown Street'}</div>
                    <div><strong>Район:</strong> ${defect.district || 'Unknown'}</div>
                    <div><strong>Серьезность:</strong> <span style="color: #ef4444">${severity.toFixed(1)}/10</span></div>
                    <div><strong>Уверенность:</strong> ${(parseFloat(defect.confidence) * 100).toFixed(0)}%</div>
                    <div><strong>Стоимость:</strong> ~${repairCost.toLocaleString()} KGS</div>
                    <div style="margin-top: 8px; padding: 8px; background: #fee2e2; border-radius: 4px; color: #991b1b;">
                        <strong>🚨 Требует немедленного ремонта!</strong>
                    </div>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent);
        marker.addTo(criticalLayer);
    });
}

// Control buttons
document.getElementById('btnMarkers').addEventListener('click', function() {
    markersLayer.addTo(map);
    if (heatmapLayer) map.removeLayer(heatmapLayer);
    map.removeLayer(criticalLayer);

    this.classList.add('active');
    document.getElementById('btnHeatmap').classList.remove('active');
    document.getElementById('btnCritical').classList.remove('active');
});

document.getElementById('btnHeatmap').addEventListener('click', function() {
    map.removeLayer(markersLayer);
    if (heatmapLayer) heatmapLayer.addTo(map);
    map.removeLayer(criticalLayer);

    this.classList.add('active');
    document.getElementById('btnMarkers').classList.remove('active');
    document.getElementById('btnCritical').classList.remove('active');
});

document.getElementById('btnCritical').addEventListener('click', function() {
    map.removeLayer(markersLayer);
    if (heatmapLayer) map.removeLayer(heatmapLayer);

    showCriticalDefects();
    criticalLayer.addTo(map);

    this.classList.add('active');
    document.getElementById('btnMarkers').classList.remove('active');
    document.getElementById('btnHeatmap').classList.remove('active');
});

// Map style controls
document.getElementById('styleStreets').addEventListener('click', function() {
    map.removeLayer(currentTileLayer);
    currentTileLayer = tileLayers.streets.addTo(map);

    document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active'));
    this.classList.add('active');
});

document.getElementById('styleSatellite').addEventListener('click', function() {
    map.removeLayer(currentTileLayer);
    currentTileLayer = tileLayers.satellite.addTo(map);

    document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active'));
    this.classList.add('active');
});

// Load data on page load
loadData();
