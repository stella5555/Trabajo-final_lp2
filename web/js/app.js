// web/js/app.js — versión FINAL
document.addEventListener("DOMContentLoaded", () => {
    console.log("🏡 Dashboard iniciado");

    const container = document.getElementById("properties-container");

    fetch("data/properties.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("No se pudo cargar properties.json");
            }
            return response.json();
        })
        .then(data => {
            console.log("📊 Propiedades cargadas:", data.length);

            // Limpiar contenedor
            container.innerHTML = "";

            // Mostrar solo las primeras 12 para no saturar
            data.slice(0, 12).forEach(property => {
    const card = document.createElement("div");
    card.className = "property-card";

    card.innerHTML = `
        <div class="property-header">
            <div class="property-district">
                <i class="fas fa-map-marker-alt"></i>
                ${property.location || "Distrito desconocido"}
            </div>
            <div class="property-score score-excelente">
                ${property.final_score?.toFixed(1) ?? "—"}
            </div>
        </div>

        <div class="property-details">
            <div class="detail-item">
                <span class="label">💰 Precio</span>
                <span class="value">S/. ${property.price_clean?.toFixed(0) ?? "—"}</span>
            </div>
            <div class="detail-item">
                <span class="label">📐 Área</span>
                <span class="value">${property.area_clean ?? "—"} m²</span>
            </div>
            <div class="detail-item">
                <span class="label">🛏 Dormitorios</span>
                <span class="value">${property.bedroom_clean ?? "—"}</span>
            </div>
        </div>

        <div class="property-breakdown">
            <span>Costo:</span> ${property.cost_score ?? "—"} |
            <span>Seguridad:</span> ${property.security_score ?? "—"} |
            <span>Servicios:</span> ${property.services_score ?? "—"}
        </div>
    `;

    container.appendChild(card);
});

        })
        .catch(error => {
            console.error("❌ Error:", error);
            container.innerHTML = `
                <div style="padding: 20px; background: #f8d7da; color: #721c24;">
                    Error cargando datos: ${error.message}
                </div>
            `;
        });
});
