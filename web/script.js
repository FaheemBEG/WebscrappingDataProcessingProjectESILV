function loadJSON(file) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            displayData(JSON.parse(xhr.responseText));
        }
    };
    xhr.open('GET', file, true);
    xhr.send();
}

function displayData(jsonData) {
    var tableBody = document.getElementById('data-table-body');

    // Utilisez une clé qui existe certainement dans votre JSON pour obtenir le nombre de jeux.
    var gameCount = Object.keys(jsonData.Title).length;

    for (var i = 0; i < gameCount; i++) {
        // Créer la ligne principale
        var mainRow = document.createElement('tr');

        // Créer une cellule pour contenir à la fois l'image et le titre
        var titleImageCell = document.createElement('td');
        titleImageCell.className = 'title-image-cell';
        titleImageCell.colSpan = '1';

        // Créer et ajouter l'image
        var img = document.createElement('img');
        img.src = jsonData.image_link && jsonData.image_link[i] ? jsonData.image_link[i] : 'path/to/default/image.png'; // Utilisez le chemin de l'image par défaut si nécessaire
        img.alt = 'Game Image';
        img.className = 'game-image';
        titleImageCell.appendChild(img);

        // Créer et ajouter le titre
        var title = document.createElement('div');
        title.textContent = jsonData.Title[i] || 'No title';
        title.className = 'game-title';
        titleImageCell.appendChild(title);

        mainRow.appendChild(titleImageCell);

        // Créer la cellule pour le reste des données
        var dataCell = document.createElement('td');
        dataCell.className = 'data-cell';
        dataCell.colSpan = '2';

        // Créer un sous-tableau pour les autres données
        var subTable = document.createElement('table');
        subTable.className = 'sub-table';

        // Ajouter les en-têtes au sous-tableau
        var thead = subTable.createTHead();
        var headerRow = thead.insertRow();
        var headers = ['Nom de la colonne', 'Valeurs', 'Impact Carbone'];
        headers.forEach(function(text) {
            var th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });

        // Ajouter les données au sous-tableau
        var tbody = subTable.createTBody();
        var categories = ['Main_Story', 'Main_+_Extra', 'Completionist', 'CPU', 'RAM', 'VIDEO_CARD', 'DEDICATED_VIDEO_RAM'];
        categories.forEach(function(category) {
            var dataRow = tbody.insertRow();
            var categoryCell = dataRow.insertCell();
            categoryCell.textContent = category;

            var valueCell = dataRow.insertCell();
            // Utiliser la clé avec des underscores pour accéder aux données
            var key = category.replace(/ /g, '_');
            valueCell.textContent = jsonData[key] && jsonData[key][i] !== undefined ? jsonData[key][i] : 'N/A';

            var impactCell = dataRow.insertCell();
            impactCell.textContent = '0'; // Mettre des zéros dans la colonne d'impact carbone
        });

        dataCell.appendChild(subTable);
        mainRow.appendChild(dataCell);

        // Ajouter la ligne principale au tableau principal
        tableBody.appendChild(mainRow);
    }
}


loadJSON('data.json');