// web/js/app.js

// ============================================
// 1. CONFIGURACIÓN INICIAL
// ============================================
const CONFIG = {
    maxProperties: 20,      // Máximo de propiedades a mostrar
    sortBy: 'final_score',  // Campo para ordenar (final_score, price_clean, etc.)
    ascending: false        // false = descendente (mejores primero)
};

// ============================================
// 2. CARGAR Y PROCESAR DATOS
// ============================================
async function loadProperties() {
    console.log("📊 Cargando datos de propiedades...");
    
    try {
        // OPCIÓN A: Cargar desde CSV (si usas scored_properties.csv)
        const response = await fetch('../data/processed/scored_properties.csv');
        const csvText = await response.text();
        const properties = parseCSVtoJSON(csvText);
        
        // OPCIÓN B: Cargar desde JSON (si usas api_enricher.py que genera JSON)
        // const response = await fetch('data/properties.json');
        // const properties = await response.json();
        
        console.log(`✅ ${properties.length} propiedades cargadas`);
        
        // Procesar y mostrar
        const processed = processProperties(properties);
        displayProperties(processed);
        
        // Actualizar estadísticas
        updateStatistics(properties);
        
    } catch (error) {
        console.error("❌ Error cargando datos:", error);
        document.getElementById('properties-container').innerHTML = `
            <div class="error-message">
                <h3>⚠️ Error cargando datos</h3>
                <p>No se pudieron cargar las propiedades. Verifica que el archivo exista.</p>
                <button onclick="loadProperties()">Reintentar</button>
            </div>
        `;
    }
}

// ============================================
// 3. FUNCIÓN PARA CONVERTIR CSV A JSON
// ============================================
function parseCSVtoJSON(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    const properties = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === '') continue;
        
        const values = lines[i].split(',');
        const property = {};
        
        for (let j = 0; j < headers.length; j++) {
            let value = values[j] || '';
            
            // Limpiar comillas si existen
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.slice(1, -1);
            }
            
            // Intentar convertir a número si es posible
            if (!isNaN(value) && value !== '') {
                property[headers[j]] = Number(value);
            } else {
                property[headers[j]] = value;
            }
        }
        
        // Solo agregar si tiene datos mínimos
        if (property.location && property.final_score !== undefined) {
            properties.push(property);
        }
    }
    
    return properties;
}

// ============================================
// 4. PROCESAR Y ORDENAR PROPIEDADES
// ============================================
function processProperties(properties) {
    // 1. Ordenar por puntaje final (mejores primero)
    properties.sort((a, b) => {
        if (CONFIG.ascending) {
            return a[CONFIG.sortBy] - b[CONFIG.sortBy];
        } else {
            return b[CONFIG.sortBy] - a[CONFIG.sortBy];
        }
    });
    
    // 2. Limitar cantidad
    const limited = properties.slice(0, CONFIG.maxProperties);
    
    // 3. Agregar formato para display
    return limited.map(prop => ({
        ...prop,
        // Formatear precio con separadores de miles
        price_formatted: prop.price_clean ? 
            `S/. ${Math.round(prop.price_clean).toLocaleString('es-PE')}` : 
            'Precio no disponible',
        
        // Formatear área
        area_formatted: prop.area_clean ? 
            `${Math.round(prop.area_clean)} m²` : 
            'Área no disponible',
        
        // Determinar color según puntaje
        score_color: getScoreColor(prop.final_score),
        
        // Extraer distrito de location
        district: extractDistrict(prop.location)
    }));
}

// ============================================
// 5. MOSTRAR PROPIEDADES EN EL HTML
// ============================================
function displayProperties(properties) {
    const container = document.getElementById('properties-container');
    
    if (!container) {
        console.error("❌ No se encontró el contenedor con id='properties-container'");
        return;
    }
    
    if (properties.length === 0) {
        container.innerHTML = '<p class="no-data">No hay propiedades para mostrar.</p>';
        return;
    }
    
    let html = '<div class="properties-grid">';
    
    properties.forEach(prop => {
        html += `
        <div class="property-card">
            <div class="property-header">
                <span class="property-district">${prop.district || 'Sin distrito'}</span>
                <span class="property-score" style="background-color: ${prop.score_color}">
                    ${prop.final_score.toFixed(1)}
                </span>
            </div>
            
            <div class="property-details">
                <div class="detail-item">
                    <span class="label">📍 Ubicación:</span>
                    <span class="value">${prop.location || 'No especificada'}</span>
                </div>
                
                <div class="detail-item">
                    <span class="label">💰 Precio:</span>
                    <span class="value">${prop.price_formatted}</span>
                </div>
                
                <div class="detail-item">
                    <span class="label">📐 Área:</span>
                    <span class="value">${prop.area_formatted}</span>
                </div>
                
                <div class="detail-item">
                    <span class="label">🛏️ Dormitorios:</span>
                    <span class="value">${prop.bedroom_clean || 'N/A'}</span>
                </div>
                
                <div class="detail-item">
                    <span class="label">🚿 Baños:</span>
                    <span class="value">${prop.bathroom_clean || 'N/A'}</span>
                </div>
            </div>
            
            <div class="property-breakdown">
                <small>Desglose: 
                <span style="color: #4CAF50;">Costo: ${prop.cost_score?.toFixed(1) || 'N/A'}</span> | 
                <span style="color: #2196F3;">Seguridad: ${prop.safety_score?.toFixed(1) || 'N/A'}</span> | 
                <span style="color: #FF9800;">Servicios: ${prop.services_score?.toFixed(1) || 'N/A'}</span>
                </small>
            </div>
        </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// ============================================
// 6. FUNCIONES AUXILIARES
// ============================================
function getScoreColor(score) {
    if (score >= 8.5) return '#4CAF50';    // Verde: excelente
    if (score >= 7.0) return '#8BC34A';    // Verde claro: bueno
    if (score >= 5.5) return '#FFC107';    // Amarillo: regular
    if (score >= 4.0) return '#FF9800';    // Naranja: bajo
    return '#F44336';                      // Rojo: muy bajo
}

function extractDistrict(location) {
    if (!location) return 'Desconocido';
    
    // Intentar extraer distrito (generalmente después de la primera coma)
    const parts = location.split(',');
    if (parts.length > 1) {
        return parts[1].trim();
    }
    return location;
}

function updateStatistics(properties) {
    if (properties.length === 0) return;
    
    const stats = {
        total: properties.length,
        avgScore: (properties.reduce((sum, p) => sum + (p.final_score || 0), 0) / properties.length).toFixed(1),
        avgPrice: Math.round(properties.reduce((sum, p) => sum + (p.price_clean || 0), 0) / properties.length),
        avgArea: Math.round(properties.reduce((sum, p) => sum + (p.area_clean || 0), 0) / properties.length)
    };
    
    // Actualizar elementos HTML si existen
    const statsElement = document.getElementById('stats-container');
    if (statsElement) {
        statsElement.innerHTML = `
            <div class="stats-card">
                <h3>📊 Estadísticas</h3>
                <p><strong>Total propiedades:</strong> ${stats.total}</p>
                <p><strong>Puntaje promedio:</strong> ${stats.avgScore}</p>
                <p><strong>Precio promedio:</strong> S/. ${stats.avgPrice.toLocaleString('es-PE')}</p>
                <p><strong>Área promedio:</strong> ${stats.avgArea} m²</p>
            </div>
        `;
    }
}

// ============================================
// 7. INICIALIZAR AL CARGAR LA PÁGINA
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Dashboard Lima Housing Analytics iniciado");
    
    // Cargar propiedades automáticamente
    loadProperties();
    
    // Agregar botón de recarga si es necesario
    const reloadBtn = document.getElementById('reload-btn');
    if (reloadBtn) {
        reloadBtn.addEventListener('click', loadProperties);
    }
});