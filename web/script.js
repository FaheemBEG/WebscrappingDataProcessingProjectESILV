let jsonData = []; // Variable globale pour stocker les données JSON

document.addEventListener('DOMContentLoaded', function() {
    loadJsonData();
});

// Chargement et stockage des données JSON
async function loadJsonData() {
    const response = await fetch('../_data/games_consumption.json');
    jsonData = await response.json();
    displayData(jsonData);
}

// Fonction d'affichage des données
function displayData(data) {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';

    data.forEach(game => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td><img src="${game.Image}" alt="${game.Title}" onError="this.onerror=null;this.src='default_image.png';"></td>
            <td>${game.Title}</td>
            <td>${game.Platforms || 'N/A'}</td>
            <td>${game['Main_Story_(Hours)'] || 'N/A'}</td>
            <td>${game.carbon_footprint_pc || 'N/A'}</td>
            <td>${game.Total_kWh_pc || 'N/A'}</td>
        `;

        tableBody.appendChild(row);
    });
}

// Recherche de jeux
function searchGames() {
    const searchText = document.getElementById('search-input').value.toLowerCase();
    const filteredData = jsonData.filter(game => game.Title.toLowerCase().includes(searchText));
    displayData(filteredData);
}

function filterByPlatform(platform) {
    const filteredData = jsonData.filter(game => {
        // Vérifie si la propriété 'Platforms' existe et n'est pas null, puis vérifie si elle inclut la plateforme spécifiée
        return game.Platforms && game.Platforms.includes(platform);
    });
    displayData(filteredData);
}


function selectOption(element) {
    // Retirer la classe 'selected-option' de tous les éléments
    document.querySelectorAll('.dropdown-content a').forEach(a => a.classList.remove('selected-option'));
    
    // Ajouter la classe 'selected-option' à l'élément cliqué
    element.classList.add('selected-option');
}
