// web/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // 1. VARIABLES GLOBALES
    // ======================
    let allProperties = [];
    let filteredProperties = [];
    let districts = new Set();
    
    // Elementos del DOM
    const elements = {
        propertiesContainer: document.getElementById('propertiesContainer'),
        districtFilter: document.getElementById('districtFilter'),
        priceFilter: document.getElementById('priceFilter'),
        priceValue: document.getElementById('priceValue'),
        scoreFilter: document.getElementById('scoreFilter'),
        scoreValue: document.getElementById('scoreValue'),
        bedroomsFilter: document.getElementById('bedroomsFilter'),
        sortSelect: document.getElementById('sortSelect'),
        resetFilters: document.getElementById('resetFilters'),
        propsCount: document.getElementById('propsCount'),
        totalProps: document.getElementById('total-props'),
        totalDistricts: document.getElementById('total-districts'),
        avgScore: document.getElementById('avg-score'),
        avgPrice: document.getElementById('avg-price'),
        dataSource: document.getElementById('dataSource'),
        topDistrictsList: document.getElementById('topDistrictsList'),
        propertyModal: document.getElementById('propertyModal'),
        modalContent: document.getElementById('modalContent'),
        closeModal: document.querySelector('.close-modal')
    };
    
    // ======================
    // 2. CARGAR DATOS
    // ======================
    async function loadProperties() {
        try {
            // En un proyecto real, cargarías desde un endpoint
            // Por ahora usamos datos estáticos o podrías cargar desde CSV
            
            // Crear datos de ejemplo basados en tu dataset
            createSampleProperties();
            
            // Actualizar estadísticas
            updateStats();
            
            // Llenar filtros
            populateFilters();
            
            // Mostrar propiedades iniciales
            applyFilters();
            
            // Mostrar top distritos
            showTopDistricts();
            
        } catch (error) {
            console.error('Error cargando propiedades:', error);
            elements.propertiesContainer.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error cargando los datos. Por favor, recarga la página.</p>
                </div>
            `;
        }
    }
    
    // ======================
    // 3. CREAR DATOS DE EJEMPLO
    // ======================
    function createSampleProperties() {
        // Basado en tu dataset combinado de 126 propiedades
        // En un proyecto real, cargarías el CSV directamente
        
        allProperties = [
            // Ejemplo de propiedades REALES (de Urbania)
            {
                id: 'URB001',
                title: 'Departamento en Miraflores',
                district: 'Miraflores',
                address: 'Av. Larco 123, Miraflores',
                price: 3500,
                area: 75,
                bedrooms: 2,
                bathrooms: 1,
                safety_score: 8.5,
                services_score: 9.0,
                cost_score: 8.2,
                final_score: 8.5,
                price_per_m2: 46.67,
                latitude: -12.120,
                longitude: -77.030,
                parking: true,
                furnished: false,
                pet_friendly: true,
                source: 'urbania_real',
                description: 'Amplio departamento cerca al malecón'
            },
            {
                id: 'URB002',
                title: 'Departamento Céntrico',
                district: 'Miraflores',
                address: 'Calle Berlín 456, Miraflores',
                price: 2800,
                area: 60,
                bedrooms: 2,
                bathrooms: 1,
                safety_score: 8.3,
                services_score: 8.8,
                cost_score: 8.5,
                final_score: 8.5,
                price_per_m2: 46.67,
                latitude: -12.118,
                longitude: -77.028,
                parking: false,
                furnished: true,
                pet_friendly: false,
                source: 'urbania_real',
                description: 'Departamento amoblado en zona comercial'
            },
            // Ejemplo de propiedades de MUESTRA (sintéticas)
            {
                id: 'PROP1001',
                title: 'Penthouse Vista al Mar',
                district: 'San Isidro',
                address: 'Av. Javier Prado 1500, San Isidro',
                price: 5000,
                area: 130,
                bedrooms: 4,
                bathrooms: 3,
                safety_score: 9.2,
                services_score: 9.9,
                cost_score: 9.6,
                final_score: 9.5,
                price_per_m2: 38.46,
                latitude: -12.104,
                longitude: -77.039,
                parking: true,
                furnished: true,
                pet_friendly: true,
                source: 'sample_data',
                description: 'Lujoso penthouse con vista panorámica'
            },
            {
                id: 'PROP1002',
                title: 'Departamento Familiar',
                district: 'La Molina',
                address: 'Av. La Molina 1200, La Molina',
                price: 3200,
                area: 90,
                bedrooms: 3,
                bathrooms: 2,
                safety_score: 8.8,
                services_score: 8.0,
                cost_score: 8.4,
                final_score: 8.6,
                price_per_m2: 35.56,
                latitude: -12.080,
                longitude: -76.950,
                parking: true,
                furnished: false,
                pet_friendly: true,
                source: 'sample_data',
                description: 'Ideal para familia, zona tranquila'
            },
            {
                id: 'PROP1003',
                title: 'Estudio Económico',
                district: 'Pueblo Libre',
                address: 'Av. Brasil 800, Pueblo Libre',
                price: 900,
                area: 35,
                bedrooms: 1,
                bathrooms: 1,
                safety_score: 7.0,
                services_score: 6.8,
                cost_score: 9.1,
                final_score: 8.1,
                price_per_m2: 25.71,
                latitude: -12.075,
                longitude: -77.065,
                parking: false,
                furnished: true,
                pet_friendly: false,
                source: 'sample_data',
                description: 'Estudio económico para estudiantes'
            },
            {
                id: 'PROP1004',
                title: 'Loft Moderno',
                district: 'Barranco',
                address: 'Bajada de Baños 250, Barranco',
                price: 1800,
                area: 55,
                bedrooms: 1,
                bathrooms: 1,
                safety_score: 7.5,
                services_score: 8.0,
                cost_score: 8.7,
                final_score: 8.3,
                price_per_m2: 32.73,
                latitude: -12.150,
                longitude: -77.022,
                parking: true,
                furnished: true,
                pet_friendly: true,
                source: 'sample_data',
                description: 'Loft estilo industrial en zona bohemia'
            }
        ];
        
        // Agregar más propiedades de ejemplo para llegar a ~20
        const sampleDistricts = ['Surco', 'Jesus Maria', 'Lince', 'San Miguel', 'Magdalena'];
        
        for (let i = 5; i <= 20; i++) {
            const district = sampleDistricts[Math.floor(Math.random() * sampleDistricts.length)];
            const price = Math.floor(Math.random() * 3000) + 1000;
            const area = Math.floor(Math.random() * 80) + 30;
            
            allProperties.push({
                id: `PROP${1000 + i}`,
                title: `Propiedad ${i} en ${district}`,
                district: district,
                address: `Calle Ejemplo ${i * 100}, ${district}`,
                price: price,
                area: area,
                bedrooms: Math.floor(Math.random() * 3) + 1,
                bathrooms: Math.max(1, Math.floor(Math.random() * 2) + 1),
                safety_score: parseFloat((6 + Math.random() * 3).toFixed(1)),
                services_score: parseFloat((6 + Math.random() * 3).toFixed(1)),
                cost_score: parseFloat((8 - (price / area / 100)).toFixed(1)),
                final_score: 0, // Se calculará después
                price_per_m2: parseFloat((price / area).toFixed(2)),
                latitude: -12.0 + Math.random() * 0.2,
                longitude: -77.0 + Math.random() * 0.2,
                parking: Math.random() > 0.5,
                furnished: Math.random() > 0.5,
                pet_friendly: Math.random() > 0.5,
                source: 'sample_data',
                description: 'Descripción de ejemplo para esta propiedad'
            });
        }
        
        // Calcular score final para todas las propiedades
        allProperties.forEach(prop => {
            if (!prop.final_score || prop.final_score === 0) {
                prop.final_score = parseFloat((
                    prop.cost_score * 0.4 + 
                    prop.safety_score * 0.4 + 
                    prop.services_score * 0.2
                ).toFixed(1));
            }
        });
        
        // Recolectar distritos únicos
        allProperties.forEach(prop => districts.add(prop.district));
    }
    
    // ======================
    // 4. ACTUALIZAR ESTADÍSTICAS
    // ======================
    function updateStats() {
        const total = allProperties.length;
        const avgScore = (allProperties.reduce((sum, p) => sum + p.final_score, 0) / total).toFixed(1);
        const avgPrice = Math.round(allProperties.reduce((sum, p) => sum + p.price, 0) / total);
        
        elements.totalProps.textContent = total;
        elements.totalDistricts.textContent = districts.size;
        elements.avgScore.textContent = avgScore;
        elements.avgPrice.textContent = `S/ ${avgPrice.toLocaleString()}`;
        
        // Contar propiedades reales vs muestra
        const realCount = allProperties.filter(p => p.source === 'urbania_real').length;
        const sampleCount = allProperties.filter(p => p.source === 'sample_data').length;
        elements.dataSource.textContent = `${total} propiedades (${realCount} reales de Urbania + ${sampleCount} muestra)`;
    }
    
    // ======================
    // 5. LLENAR FILTROS
    // ======================
    function populateFilters() {
        // Llenar selector de distritos
        elements.districtFilter.innerHTML = '<option value="all">Todos los distritos</option>';
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            elements.districtFilter.appendChild(option);
        });
        
        // Configurar eventos de filtros
        elements.priceFilter.addEventListener('input', function() {
            elements.priceValue.textContent = `S/ ${this.value}`;
            applyFilters();
        });
        
        elements.scoreFilter.addEventListener('input', function() {
            elements.scoreValue.textContent = this.value;
            applyFilters();
        });
        
        elements.districtFilter.addEventListener('change', applyFilters);
        elements.bedroomsFilter.addEventListener('change', applyFilters);
        elements.sortSelect.addEventListener('change', applyFilters);
        elements.resetFilters.addEventListener('click', resetFilters);
        
        // Configurar modal
        elements.closeModal.addEventListener('click', () => {
            elements.propertyModal.style.display = 'none';
        });
        
        window.addEventListener('click', (event) => {
            if (event.target === elements.propertyModal) {
                elements.propertyModal.style.display = 'none';
            }
        });
    }
    
    // ======================
    // 6. APLICAR FILTROS
    // ======================
    function applyFilters() {
        const selectedDistrict = elements.districtFilter.value;
        const maxPrice = parseInt(elements.priceFilter.value);
        const minScore = parseFloat(elements.scoreFilter.value);
        const minBedrooms = parseInt(elements.bedroomsFilter.value);
        const sortBy = elements.sortSelect.value;
        
        // Filtrar propiedades
        filteredProperties = allProperties.filter(property => {
            // Filtro por distrito
            if (selectedDistrict !== 'all' && property.district !== selectedDistrict) {
                return false;
            }
            
            // Filtro por precio
            if (property.price > maxPrice) {
                return false;
            }
            
            // Filtro por score
            if (property.final_score < minScore) {
                return false;
            }
            
            // Filtro por habitaciones
            if (minBedrooms > 0 && property.bedrooms < minBedrooms) {
                return false;
            }
            
            return true;
        });
        
        // Ordenar propiedades
        switch (sortBy) {
            case 'score':
                filteredProperties.sort((a, b) => b.final_score - a.final_score);
                break;
            case 'price-low':
                filteredProperties.sort((a, b) => a.price - b.price);
                break;
            case 'price-high':
                filteredProperties.sort((a, b) => b.price - a.price);
                break;
            case 'area':
                filteredProperties.sort((a, b)=> b.area - a.area);
                break;
            case 'district':
                filteredProperties.sort((a, b) => a.district.localeCompare(b.district));
                break;
        }
        
        // Actualizar contador
        elements.propsCount.textContent = filteredProperties.length;
        
        // Renderizar propiedades
        renderProperties();
    }
    
    // ======================
    // 7. RENDERIZAR PROPIEDADES
    // ======================
    function renderProperties() {
        if (filteredProperties.length === 0) {
            elements.propertiesContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>No se encontraron propiedades</h3>
                    <p>Prueba ajustando los filtros</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        filteredProperties.forEach(property => {
            // Determinar icono de fuente
            const sourceIcon = property.source === 'urbania_real' 
                ? '<i class="fas fa-check-circle"></i> Real'
                : '<i class="fas fa-database"></i> Muestra';
            
            const sourceClass = property.source === 'urbania_real' ? 'source-real' : 'source-sample';
            
            html += `
                <div class="property-card" data-id="${property.id}">
                    <div class="property-header">
                        <div>
                            <div class="property-district">
                                <i class="fas fa-map-marker-alt"></i>
                                ${property.district}
                            </div>
                            <div class="property-address">
                                <i class="fas fa-home"></i>
                                ${property.address}
                            </div>
                        </div>
                        <div class="property-price">
                            S/ ${property.price.toLocaleString()}
                        </div>
                    </div>
                    
                    <div class="property-body">
                        <div class="property-features">
                            <div class="feature">
                                <i class="fas fa-ruler-combined"></i>
                                <div class="feature-value">${property.area}</div>
                                <div class="feature-label">m²</div>
                            </div>
                            <div class="feature">
                                <i class="fas fa-bed"></i>
                                <div class="feature-value">${property.bedrooms}</div>
                                <div class="feature-label">Hab</div>
                            </div>
                            <div class="feature">
                                <i class="fas fa-bath"></i>
                                <div class="feature-value">${property.bathrooms}</div>
                                <div class="feature-label">Baños</div>
                            </div>
                        </div>
                        
                        <div class="property-scores">
                            <div class="score-item">
                                <div class="score-label">Seguridad</div>
                                <div class="score-value">${property.safety_score}</div>
                            </div>
                            <div class="score-item">
                                <div class="score-label">Servicios</div>
                                <div class="score-value">${property.services_score}</div>
                            </div>
                            <div class="score-item">
                                <div class="score-label">Costo</div>
                                <div class="score-value">${property.cost_score}</div>
                            </div>
                            <div class="score-item">
                                <div class="score-label">FINAL</div>
                                <div class="score-value score-final">${property.final_score}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="property-footer">
                        <div class="property-source ${sourceClass}">
                            ${sourceIcon}
                        </div>
                        <button class="view-details" onclick="showPropertyDetails('${property.id}')">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </button>
                    </div>
                </div>
            `;
        });
        
        elements.propertiesContainer.innerHTML = html;
    }
    
    // ======================
    // 8. MOSTRAR DETALLES DE PROPIEDAD
    // ======================
    window.showPropertyDetails = function(propertyId) {
        const property = allProperties.find(p => p.id === propertyId);
        if (!property) return;
        
        const amenities = [];
        if (property.parking) amenities.push('Estacionamiento');
        if (property.furnished) amenities.push('Amueblado');
        if (property.pet_friendly) amenities.push('Mascotas permitidas');
        
        elements.modalContent.innerHTML = `
            <div class="modal-property">
                <div class="modal-header">
                    <h2><i class="fas fa-home"></i> ${property.title}</h2>
                    <div class="modal-price">S/ ${property.price.toLocaleString()}</div>
                </div>
                
                <div class="modal-info-grid">
                    <div class="info-card">
                        <h3><i class="fas fa-map-marker-alt"></i> Ubicación</h3>
                        <p><strong>Distrito:</strong> ${property.district}</p>
                        <p><strong>Dirección:</strong> ${property.address}</p>
                        <p><strong>Coordenadas:</strong> ${property.latitude}, ${property.longitude}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3><i class="fas fa-info-circle"></i> Características</h3>
                        <p><strong>Área:</strong> ${property.area} m² (S/ ${property.price_per_m2}/m²)</p>
                        <p><strong>Habitaciones:</strong> ${property.bedrooms}</p>
                        <p><strong>Baños:</strong> ${property.bathrooms}</p>
                        <p><strong>Amenidades:</strong> ${amenities.join(', ') || 'Ninguna'}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3><i class="fas fa-chart-bar"></i> Puntajes Detallados</h3>
                        <div class="score-breakdown">
                            <div class="score-row">
                                <span>Seguridad:</span>
                                <span>${property.safety_score}/10 × 0.4 = ${(property.safety_score * 0.4).toFixed(2)}</span>
                            </div>
                            <div class="score-row">
                                <span>Servicios:</span>
                                <span>${property.services_score}/10 × 0.2 = ${(property.services_score * 0.2).toFixed(2)}</span>
                            </div>
                            <div class="score-row">
                                <span>Costo:</span>
                                <span>${property.cost_score}/10 × 0.4 = ${(property.cost_score * 0.4).toFixed(2)}</span>
                            </div>
                            <div class="score-row total">
                                <span><strong>SCORE FINAL:</strong></span>
                                <span><strong>${property.final_score}/10</strong></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <h3><i class="fas fa-database"></i> Fuente de Datos</h3>
                        <p><strong>Origen:</strong> ${property.source === 'urbania_real' ? 'Extraído de Urbania.pe' : 'Datos de muestra sintéticos'}</p>
                        <p><strong>ID:</strong> ${property.id}</p>
                        <p><strong>Descripción:</strong> ${property.description}</p>
                    </div>
                </div>
                
                <div class="modal-formula">
                    <h3><i class="fas fa-calculator"></i> Fórmula de Scoring Aplicada</h3>
                    <div class="formula-display">
                        <code>
                            Score Final = (Costo × 0.4) + (Seguridad × 0.4) + (Servicios × 0.2)<br>
                            ${property.final_score} = (${property.cost_score} × 0.4) + (${property.safety_score} × 0.4) + (${property.services_score} × 0.2)
                        </code>
                    </div>
                </div>
            </div>
        `;
        
        elements.propertyModal.style.display = 'flex';
    };
    
    // ======================
    // 9. MOSTRAR TOP DISTRITOS
    // ======================
    function showTopDistricts() {
        // Calcular score promedio por distrito
        const districtScores = {};
        
        allProperties.forEach(property => {
            if (!districtScores[property.district]) {
                districtScores[property.district] = {
                    total: 0,
                    count: 0,
                    avg: 0
                };
            }
            districtScores[property.district].total += property.final_score;
            districtScores[property.district].count += 1;
        });
        
        // Calcular promedios
        Object.keys(districtScores).forEach(district => {
            districtScores[district].avg = districtScores[district].total / districtScores[district].count;
        });
        
        // Ordenar por score promedio
        const sortedDistricts = Object.keys(districtScores)
            .map(district => ({
                name: district,
                score: districtScores[district].avg
            }))
            .sort((a, b) => b.score - a.score)
            .slice(0, 5);
        
        // Renderizar
        let html = '';
        sortedDistricts.forEach((district, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;
            html += `
                <div class="district-item">
                    <div class="district-name">
                        ${medal} ${district.name}
                    </div>
                    <div class="district-score">
                        ${district.score.toFixed(1)}
                    </div>
                </div>
            `;
        });
        
        elements.topDistrictsList.innerHTML = html;
    }
    
    // ======================
    // 10. REINICIAR FILTROS
    // ======================
    function resetFilters() {
        elements.districtFilter.value = 'all';
        elements.priceFilter.value = 7000;
        elements.priceValue.textContent = 'S/ 7000';
        elements.scoreFilter.value = 5;
        elements.scoreValue.textContent = '5.0';
        elements.bedroomsFilter.value = '0';
        elements.sortSelect.value = 'score';
        
        applyFilters();
    }
    
    // ======================
    // 11. INICIALIZAR
    // ======================
    function init() {
        console.log('🚀 Dashboard Lima Housing Analytics iniciado');
        loadProperties();
    }
    
    // Iniciar la aplicación
    init();
});