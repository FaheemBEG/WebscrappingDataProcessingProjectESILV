let jsonData = []; // Var to stock jsonData

document.addEventListener('DOMContentLoaded', function() {
    loadJsonData();
});

// Loading games .json file
async function loadJsonData() {
    const response = await fetch('../_data/games_consumption.json');
    jsonData = await response.json();
    displayData(jsonData);
}

// Data displaying function
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

// searchGames function 
function searchGames() {
    const searchText = document.getElementById('search-input').value.toLowerCase();
    const filteredData = jsonData.filter(game => game.Title.toLowerCase().includes(searchText));
    displayData(filteredData);
}

function filterByPlatform(platform) {
    const filteredData = jsonData.filter(game => {
        return game.Platforms && game.Platforms.includes(platform);
    });
    displayData(filteredData);
}


function selectOption(element) {
    document.querySelectorAll('.dropdown-content a').forEach(a => a.classList.remove('selected-option'));
    
    element.classList.add('selected-option');
}
