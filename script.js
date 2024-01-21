var jsonData;

function displayData(jsonData) {
    var tableBody = document.getElementById('data-table-body');

    var gameCount = Object.keys(jsonData.Title).length;

    for (var i = 0; i < gameCount; i++) {
        var mainRow = document.createElement('tr');

        // Créer une cellule pour l'image
        var imageCell = document.createElement('td');
        var img = document.createElement('img');
        img.src = jsonData['Image'][i] ? jsonData['Image'][i] : 'default_image.png';
        img.alt = 'Game Image';
        img.className = 'game-image';
        imageCell.appendChild(img);
        mainRow.appendChild(imageCell);

        // Créer une cellule pour le titre du jeu
        var titleCell = document.createElement('td');
        titleCell.textContent = Object.values(jsonData.Title)[i] || 'No title provided';
        mainRow.appendChild(titleCell);

        // Créer une cellule pour l'impact carbone
        var carbonImpactCell = document.createElement('td');
        var impactCarboneValue = jsonData['impact_carbone'][i] || '0';
        carbonImpactCell.innerHTML = convertToStars(impactCarboneValue);
        var sortValue = getSortValue(impactCarboneValue);
        carbonImpactCell.setAttribute('data-sort-value', sortValue);
        mainRow.appendChild(carbonImpactCell);

        tableBody.appendChild(mainRow);
    }

    var carbonImpactHeader = document.getElementById("carbon-impact-header");
    if (carbonImpactHeader) {
        carbonImpactHeader.addEventListener("click", sortTableByCarbonImpact);
    }
}

function loadJSON(file) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            jsonData = JSON.parse(xhr.responseText);
            displayData(jsonData);
            
        }
    };
    xhr.open('GET', file, true);
    xhr.send();
}

loadJSON('data/games_full_2.json');



function extractUniquePlatforms(jsonData) {
    var platforms = [];
    for (var key in jsonData.Platforms) {
        var platformList = jsonData.Platforms[key].split(', ');
        platforms = platforms.concat(platformList);
    }
    return [...new Set(platforms)];
}

// Fonction pour afficher les options de plateforme dans la liste déroulante
function displayPlatformOptions(jsonData) {
    var dropdown = document.querySelector('.platform-dropdown');
    var uniquePlatforms = extractUniquePlatforms(jsonData);

    var allOption = document.createElement('a');
    allOption.href = "#";
    allOption.textContent = "Tous les plateformes";
    allOption.onclick = function() {
        filterByPlatform('Tous les plateformes');
        selectOption(allOption);
    };
    dropdown.appendChild(allOption);

    uniquePlatforms.forEach(function(platform) {
        var option = document.createElement('a');
        option.href = "#";
        option.textContent = platform;
        option.onclick = function() {
            filterByPlatform(platform);
            selectOption(option);
        };
        dropdown.appendChild(option);
    });
}

// Fonction pour gérer la sélection d'une option
function selectOption(option) {
    var options = document.querySelectorAll('.platform-dropdown a');
    options.forEach(function(opt) {
        opt.classList.remove('selected-option');
    });

    option.classList.add('selected-option');
}

function filterByPlatform(platform) {
    var rows = document.querySelectorAll('.main-table tbody tr');

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var titleCell = row.cells[1];
        var gameTitle = titleCell.textContent.trim();

        var gameIndex = null;
        for (var key in jsonData.Title) {
            if (jsonData.Title[key] === gameTitle) {
                gameIndex = key;
                break;
            }
        }

        if (gameIndex !== null) {
            if (jsonData.Platforms[gameIndex]) {
                var platforms = jsonData.Platforms[gameIndex].split(', ');
                if (platform === "Tous les plateformes" || platforms.includes(platform)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        }
    }
}


function searchGames() {
    var searchTerm = document.getElementById('search-input').value.toLowerCase();
    var rows = document.querySelectorAll('.main-table tbody tr');

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var titleCell = row.cells[1];
        var gameTitle = titleCell.textContent.toLowerCase();

        if (gameTitle.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

function convertToStars(impactCarbone) {
    if (impactCarbone === -1) {
        return 'Pas de données disponible';
    }

    var rating = parseFloat(impactCarbone);
    var fullStars = Math.floor(rating);
    var hasHalfStar = rating - fullStars >= 0.5;
    var emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    var starsHtml = '';
    for (var i = 0; i < fullStars; i++) {
        starsHtml += '<span class="star">&#9733;</span>'; // Étoile pleine
    }
    if (hasHalfStar) {
        starsHtml += '<span class="star">&#9733;&#9734;</span>'; // Demi-étoile
    }
    for (var i = 0; i < emptyStars; i++) {
        starsHtml += '<span class="star">&#9734;</span>'; // Étoile vide
    }

    return starsHtml;
}

// Cette fonction convertit la valeur d'impact carbone en un nombre pour le tri
function getSortValue(impactCarbone) {
    if (impactCarbone === -1) {
        return -1;
    } else {
        return parseFloat(impactCarbone);
    }
}

// Fonction pour trier le tableau
function sortTableByCarbonImpact() {
    var table = document.querySelector(".main-table");
    var rows = Array.from(table.getElementsByTagName("TR")).slice(1);

    rows.sort(function(a, b) {
        var valA = parseFloat(a.cells[2].getAttribute('data-sort-value'));
        var valB = parseFloat(b.cells[2].getAttribute('data-sort-value'));

        return valB - valA;
    });

    var tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}