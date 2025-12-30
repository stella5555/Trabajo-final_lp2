
class Dashboard {
    constructor() {
        this.properties = [];
        this.filteredProperties = [];
        this.filters = {
            district: 'all',
            maxPrice: 50000,
            minScore: 0,
            bedrooms: 0,  // CAMBIÉ de minBedrooms a bedrooms (0 = cualquiera, 1-4 = exacto, 5 = 5+)
            sortBy: 'final_score_desc'
        };
    }
    
    async init() {
        console.log('🚀 Iniciando Lima Housing Analytics Dashboard');
        
        // Mostrar loading
        this.showLoading();
        
        try {
            // Cargar datos
            await this.loadData();
            
            // Configurar interfaz
            this.renderStats();
            this.setupFilters();
            this.renderTopDistricts();
            this.renderProperties();
            
            console.log('✅ Dashboard cargado con', this.properties.length, 'propiedades');
        } catch (error) {
            this.showError('Error cargando los datos: ' + error.message);
        }
    }
    
    showLoading() {
        const container = document.getElementById('properties-container');
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin fa-3x"></i>
                <p>Cargando ${this.properties.length || '677'} propiedades reales de Lima...</p>
            </div>
        `;
    }
    
    showError(message) {
        const container = document.getElementById('properties-container');
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="btn-retry">
                    <i class="fas fa-redo"></i> Reintentar
                </button>
            </div>
        `;
    }
    
    async loadData() {
        try {
            const response = await fetch('data/properties.json');
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status}`);
            }
            
            this.properties = await response.json();
            this.filteredProperties = [...this.properties];
            
            // Limpiar propiedades sin datos esenciales
            this.properties = this.properties.filter(p => 
                p && p.district && p.price_clean && p.final_score
            );
            
            console.log(`📊 ${this.properties.length} propiedades cargadas`);
            
        } catch (error) {
            console.error('Error cargando datos:', error);
            throw error;
        }
    }
    
    renderStats() {
        if (this.properties.length === 0) return;
        
        // Calcular estadísticas
        const totalProps = this.properties.length;
        const districts = [...new Set(this.properties.map(p => p.district))].length;
        
        const avgPrice = this.properties.reduce((sum, p) => 
            sum + (p.price_clean || 0), 0) / totalProps;
        
        const avgScore = this.properties.reduce((sum, p) => 
            sum + (p.final_score || 0), 0) / totalProps;
        
        // Actualizar DOM
        document.getElementById('total-props').textContent = totalProps.toLocaleString('es-PE');
        document.getElementById('total-districts').textContent = districts;
        document.getElementById('avg-score').textContent = avgScore.toFixed(1);
        document.getElementById('avg-price').textContent = `S/ ${Math.round(avgPrice).toLocaleString('es-PE')}`;
        
        // Actualizar contador
        this.updatePropsCount();
    }
    
    updatePropsCount() {
        const count = this.filteredProperties.length;
        document.getElementById('propsCount').textContent = count.toLocaleString('es-PE');
    }
    
    setupFilters() {
        // 1. DISTRITOS
        const districts = [...new Set(this.properties
            .map(p => p.district)
            .filter(d => d && d.trim() !== '')
            .sort((a, b) => a.localeCompare(b, 'es')))];
        
        const districtFilter = document.getElementById('districtFilter');
        districtFilter.innerHTML = '<option value="all">Todos los distritos</option>';
        
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtFilter.appendChild(option);
        });
        
        districtFilter.addEventListener('change', (e) => {
            this.filters.district = e.target.value;
            this.applyFilters();
        });
        
        // 2. PRECIO MÁXIMO
        const priceFilter = document.getElementById('priceFilter');
        const priceValue = document.getElementById('priceValue');
        
        // Calcular precio máximo real (redondear al múltiplo de 5000)
        const maxPrice = Math.max(...this.properties.map(p => p.price_clean || 0));
        const roundedMax = Math.ceil(maxPrice / 5000) * 5000;
        
        priceFilter.max = roundedMax;
        priceFilter.value = roundedMax;
        priceValue.textContent = `S/ ${roundedMax.toLocaleString('es-PE')}`;
        
        priceFilter.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            priceValue.textContent = `S/ ${value.toLocaleString('es-PE')}`;
            this.filters.maxPrice = value;
            this.applyFilters();
        });
        
        // 3. SCORE MÍNIMO
        const scoreFilter = document.getElementById('scoreFilter');
        const scoreValue = document.getElementById('scoreValue');
        
        scoreFilter.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            scoreValue.textContent = value.toFixed(1);
            this.filters.minScore = value;
            this.applyFilters();
        });
        
        // 4. HABITACIONES - CAMBIADO A FILTRO EXACTO
        const bedroomsFilter = document.getElementById('bedroomsFilter');
        bedroomsFilter.addEventListener('change', (e) => {
            const value = e.target.value;
            this.filters.bedrooms = value === "0" ? 0 : parseInt(value) || 0;
            console.log(`Filtro habitaciones: ${this.filters.bedrooms}`);
            this.applyFilters();
        });
        
        // 5. ORDENAMIENTO
        const sortSelect = document.getElementById('sortSelect');
        sortSelect.addEventListener('change', (e) => {
            this.filters.sortBy = e.target.value;
            this.applyFilters();
        });
        
        // 6. REINICIAR FILTROS
        document.getElementById('resetFilters').addEventListener('click', () => {
            this.resetFilters();
        });
    }
    
    resetFilters() {
        // Restablecer valores - ACTUALIZADO
        this.filters = {
            district: 'all',
            maxPrice: parseInt(document.getElementById('priceFilter').max),
            minScore: 0,
            bedrooms: 0,  // CAMBIÉ
            sortBy: 'final_score_desc'
        };
        
        // Restablecer UI
        document.getElementById('districtFilter').value = 'all';
        
        const priceFilter = document.getElementById('priceFilter');
        priceFilter.value = this.filters.maxPrice;
        document.getElementById('priceValue').textContent = 
            `S/ ${this.filters.maxPrice.toLocaleString('es-PE')}`;
        
        document.getElementById('scoreFilter').value = 0;
        document.getElementById('scoreValue').textContent = '0.0';
        document.getElementById('bedroomsFilter').value = '0';  // Esto debe coincidir con tu HTML
        document.getElementById('sortSelect').value = 'final_score_desc';
        
        // Aplicar
        this.applyFilters();
        
        // Notificación
        this.showNotification('Filtros reiniciados');
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Mostrar
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    applyFilters() {
        let filtered = [...this.properties];
        
        console.log("🔍 Aplicando filtros:", this.filters);
        
        // 1. Distrito
        if (this.filters.district !== 'all') {
            filtered = filtered.filter(p => 
                p.district === this.filters.district
            );
        }
        
        // 2. Precio máximo
        filtered = filtered.filter(p => 
            (p.price_clean || 0) <= this.filters.maxPrice
        );
        
        // 3. Score mínimo
        filtered = filtered.filter(p => 
            (p.final_score || 0) >= this.filters.minScore
        );
        
        // 4. Habitaciones - FILTRO EXACTO (MODIFICADO)
        if (this.filters.bedrooms > 0) {
            console.log(`Filtrando por habitaciones: ${this.filters.bedrooms}`);
            
            filtered = filtered.filter(p => {
                const bedrooms = p.bedroom_clean || 0;
                
                // Si el filtro es 5, buscar 5 o más habitaciones
                if (this.filters.bedrooms === 5) {
                    return bedrooms >= 5;
                } 
                // Para valores 1-4, buscar cantidad exacta
                else {
                    return bedrooms === this.filters.bedrooms;
                }
            });
        }
        
        console.log(`📊 Resultados después de filtros: ${filtered.length} propiedades`);
        
        // 5. Ordenar
        this.filteredProperties = this.sortProperties(filtered);
        
        // 6. Renderizar
        this.renderProperties();
        this.updatePropsCount();
    }
    
    sortProperties(properties) {
        const sorted = [...properties];
        
        switch (this.filters.sortBy) {
            case 'final_score_desc':
                sorted.sort((a, b) => (b.final_score || 0) - (a.final_score || 0));
                break;
            case 'price_clean_asc':
                sorted.sort((a, b) => (a.price_clean || 0) - (b.price_clean || 0));
                break;
            case 'price_clean_desc':
                sorted.sort((a, b) => (b.price_clean || 0) - (a.price_clean || 0));
                break;
            case 'area_clean_desc':
                sorted.sort((a, b) => (b.area_clean || 0) - (a.area_clean || 0));
                break;
            default:
                sorted.sort((a, b) => (b.final_score || 0) - (a.final_score || 0));
        }
        
        return sorted;
    }
    
    renderProperties() {
        const container = document.getElementById('properties-container');
        
        if (this.filteredProperties.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search fa-3x"></i>
                    <h3>No se encontraron propiedades</h3>
                    <p>Prueba con filtros diferentes o reinicia los filtros.</p>
                    <button onclick="dashboard.resetFilters()" class="btn-primary">
                        <i class="fas fa-redo"></i> Reiniciar filtros
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        // Mostrar máximo 50 propiedades
        const propertiesToShow = this.filteredProperties.slice(0, 50);
        
        propertiesToShow.forEach(property => {
            const card = this.createPropertyCard(property);
            container.appendChild(card);
        });
        
        // Mostrar advertencia si hay más
        if (this.filteredProperties.length > 50) {
            const warning = document.createElement('div');
            warning.className = 'results-warning';
            warning.innerHTML = `
                <i class="fas fa-info-circle"></i>
                Mostrando 50 de ${this.filteredProperties.length} propiedades.
                Usa filtros más específicos para ver menos resultados.
            `;
            container.appendChild(warning);
        }
    }
    
    createPropertyCard(property) {
        const card = document.createElement('div');
        card.className = 'property-card';
        
        // Calcular clases de score
        const finalScore = property.final_score || 0;
        let scoreClass = 'score-bajo';
        if (finalScore >= 8.5) scoreClass = 'score-excelente';
        else if (finalScore >= 7.5) scoreClass = 'score-bueno';
        else if (finalScore >= 6.5) scoreClass = 'score-medio';
        
        // Formatear datos
        const formattedPrice = property.price_clean 
            ? `S/ ${Math.round(property.price_clean).toLocaleString('es-PE')}` 
            : '—';
        
        const area = property.area_clean 
            ? `${Math.round(property.area_clean).toLocaleString('es-PE')} m²`
            : '—';
        
        const bedrooms = property.bedroom_clean || '—';
        const bathrooms = property.bathroom_clean || '—';
        
        // Obtener imagen del distrito (si existe)
        const districtImage = this.getDistrictImage(property.district);
        
        card.innerHTML = `
            <div class="property-image">
                <img src="${districtImage}" alt="${property.district}" 
                     onerror="this.src='assets/img/default.jpg'">
                <div class="property-score-overlay ${scoreClass}">
                    ${finalScore.toFixed(1)}
                </div>
            </div>
            
            <div class="property-content">
                <div class="property-header">
                    <h3 class="property-district">
                        <i class="fas fa-map-marker-alt"></i>
                        ${property.district || 'Distrito no especificado'}
                    </h3>
                    <div class="property-final-score ${scoreClass}">
                        ${finalScore.toFixed(1)}
                    </div>
                </div>
                
                <p class="property-title">${property.title || ''}</p>
                <p class="property-address">${this.shortenText(property.location || '', 50)}</p>
                
                <div class="property-details">
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon"><i class="fas fa-money-bill-wave"></i></span>
                            <span class="detail-label">Precio</span>
                            <span class="detail-value">${formattedPrice}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon"><i class="fas fa-ruler-combined"></i></span>
                            <span class="detail-label">Área</span>
                            <span class="detail-value">${area}</span>
                        </div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon"><i class="fas fa-bed"></i></span>
                            <span class="detail-label">Dorm.</span>
                            <span class="detail-value">${bedrooms}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon"><i class="fas fa-bath"></i></span>
                            <span class="detail-label">Baños</span>
                            <span class="detail-value">${bathrooms}</span>
                        </div>
                    </div>
                </div>
                
                <div class="score-breakdown">
                    <h4><i class="fas fa-chart-pie"></i> Desglose del Score</h4>
                    
                    <div class="score-item">
                        <div class="score-label">
                            <span class="score-name">💰 Costo</span>
                            <span class="score-value">${(property.cost_score || 0).toFixed(1)}</span>
                        </div>
                        <div class="score-bar">
                            <div class="bar-fill" style="width: ${(property.cost_score || 0) * 10}%"></div>
                        </div>
                    </div>
                    
                    <div class="score-item">
                        <div class="score-label">
                            <span class="score-name">🛡️ Seguridad</span>
                            <span class="score-value">${(property.safety_score || 0).toFixed(1)}</span>
                        </div>
                        <div class="score-bar">
                            <div class="bar-fill" style="width: ${(property.safety_score || 0) * 10}%"></div>
                        </div>
                    </div>
                    
                    <div class="score-item">
                        <div class="score-label">
                            <span class="score-name">🏪 Servicios</span>
                            <span class="score-value">${(property.services_score || 0).toFixed(1)}</span>
                        </div>
                        <div class="score-bar">
                            <div class="bar-fill" style="width: ${(property.services_score || 0) * 10}%"></div>
                        </div>
                    </div>
                    
                    <div class="score-formula">
                        <small>
                            <i class="fas fa-calculator"></i>
                            Final = (${(property.cost_score || 0).toFixed(1)}×0.4) + 
                            (${(property.safety_score || 0).toFixed(1)}×0.4) + 
                            (${(property.services_score || 0).toFixed(1)}×0.2)
                        </small>
                    </div>
                </div>
                
                <div class="property-footer">
                    <a href="${property.url || '#'}" target="_blank" class="btn-view-details">
                        <i class="fas fa-external-link-alt"></i> Ver en Properati
                    </a>
                    <span class="publish-date">
                        <i class="far fa-calendar-alt"></i>
                        ${property.date_pub || 'Fecha no disponible'}
                    </span>
                </div>
            </div>
        `;
        
        return card;
    }
    
    getDistrictImage(districtName) {
        if (!districtName) return 'assets/img/default.jpg';
        
        // Normalizar nombre para imagen
        const normalized = districtName.toLowerCase()
            .replace(/ /g, '-')
            .replace(/ñ/g, 'n')
            .replace(/[áéíóú]/g, '')
            .replace(/[^a-z0-9-]/g, '');
        
        return `assets/img/${normalized}.jpg`;
    }
    
    shortenText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    renderTopDistricts() {
        const container = document.getElementById('topDistrictsList');
        
        if (this.properties.length === 0) {
            container.innerHTML = `
                <div class="district-item">
                    <div class="district-name">Cargando...</div>
                    <div class="district-score">—</div>
                </div>
            `;
            return;
        }
        
        // Calcular score promedio por distrito
        const districtStats = {};
        
        this.properties.forEach(property => {
            if (!property.district) return;
            
            const district = property.district;
            const score = property.final_score || 0;
            
            if (!districtStats[district]) {
                districtStats[district] = {
                    totalScore: 0,
                    count: 0,
                    avgPrice: 0
                };
            }
            
            districtStats[district].totalScore += score;
            districtStats[district].avgPrice += property.price_clean || 0;
            districtStats[district].count += 1;
        });
        
        // Calcular promedios
        Object.keys(districtStats).forEach(district => {
            districtStats[district].avgScore = districtStats[district].totalScore / districtStats[district].count;
            districtStats[district].avgPrice = districtStats[district].avgPrice / districtStats[district].count;
        });
        
        // Convertir a array y ordenar por score promedio
        const topDistricts = Object.entries(districtStats)
            .filter(([_, stats]) => stats.count >= 3) // Al menos 3 propiedades
            .map(([district, stats]) => ({
                district,
                avgScore: stats.avgScore,
                avgPrice: stats.avgPrice,
                count: stats.count
            }))
            .sort((a, b) => b.avgScore - a.avgScore)
            .slice(0, 5);
        
        // Renderizar
        container.innerHTML = '';
        
        topDistricts.forEach((item, index) => {
            const districtItem = document.createElement('div');
            districtItem.className = 'district-item';
            
            // Determinar medalla
            let medal = '';
            if (index === 0) medal = '🥇';
            else if (index === 1) medal = '🥈';
            else if (index === 2) medal = '🥉';
            
            // Determinar clase de score
            let scoreClass = 'score-bajo';
            if (item.avgScore >= 8.5) scoreClass = 'score-excelente';
            else if (item.avgScore >= 7.5) scoreClass = 'score-bueno';
            else if (item.avgScore >= 6.5) scoreClass = 'score-medio';
            
            districtItem.innerHTML = `
                <div class="district-info">
                    <div class="district-rank">${medal}</div>
                    <div class="district-name">${item.district}</div>
                </div>
                <div class="district-stats">
                    <div class="district-score ${scoreClass}">${item.avgScore.toFixed(1)}</div>
                    <small>${item.count} props</small>
                </div>
            `;
            
            container.appendChild(districtItem);
        });
    }
}

// Crear instancia global
window.dashboard = new Dashboard();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard.init();
});