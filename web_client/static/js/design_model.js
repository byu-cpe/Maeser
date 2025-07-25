/*
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

let fileGroupCount = 0;
function addFileGroup() {
    const container = document.getElementById('file-groups-container');

    const groupDiv = document.createElement('div');
    groupDiv.className = 'file-group';
    groupDiv.dataset.groupId = fileGroupCount;

    // Inner content wrapper
    const innerDiv = document.createElement('div');
    innerDiv.className = 'file-group-content';

    // Group name
    const nameLabel = document.createElement('label');
    nameLabel.textContent = 'Dataset Name:';
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.name = `file_groups[${fileGroupCount}][name]`;
    nameInput.required = true;

    // File input
    const fileLabel = document.createElement('label');
    fileLabel.textContent = 'Upload PDF Files:';
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.name = `file_groups[${fileGroupCount}][files]`;
    fileInput.accept = '.pdf';
    fileInput.multiple = true;
    fileInput.required = true;
    fileInput.addEventListener('change', updateFileList)
    const fileListContainer = document.createElement('div');
    fileListContainer.className = 'file-list';
    let dt = new DataTransfer();

    function updateFileList() {
        Array.from(fileInput.files).forEach(file => {
            dt.items.add(file);
        });
        fileInput.files = dt.files;
        renderFileList();
    }
    
    function renderFileList() {
    // clear out old entries
    fileListContainer.innerHTML = '';

    Array.from(dt.files).forEach((file, idx) => {
        const entry = document.createElement('div');
        entry.className = 'file-entry';

        // file name
        const nameSpan = document.createElement('span');
        nameSpan.textContent = file.name;
        entry.appendChild(nameSpan);

        // remove button
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = 'Remove';
        btn.addEventListener('click', () => {
            dt.items.remove(idx);
            fileInput.files = dt.files;
            renderFileList();
        });
        entry.appendChild(btn);

        fileListContainer.appendChild(entry);
    });
    }

    // Delete button
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'remove-button';
    removeButton.textContent = 'X';
    removeButton.onclick = () => container.removeChild(groupDiv);

    // Assemble
    innerDiv.appendChild(nameLabel);
    innerDiv.appendChild(document.createElement('br'));
    innerDiv.appendChild(nameInput);
    innerDiv.appendChild(document.createElement('br'));
    innerDiv.appendChild(document.createElement('br'));
    innerDiv.appendChild(fileLabel);
    innerDiv.appendChild(document.createElement('br'));
    innerDiv.appendChild(fileInput);
    innerDiv.appendChild(document.createElement('br'));
    innerDiv.appendChild(fileListContainer);

    groupDiv.appendChild(innerDiv);
    groupDiv.appendChild(removeButton);
    container.appendChild(groupDiv);

    fileGroupCount++;
}
            

function addRule() {
    const container = document.getElementById('rules-container');

    // Create wrapper div for rule input and delete button
    const ruleDiv = document.createElement('div');
    ruleDiv.className = 'rule-entry';

    // Create input
    const input = document.createElement('input');
    input.className = 'rule-input';
    input.type = 'text';
    input.name = 'rules[]';
    input.placeholder = 'Enter rule';

    // Create delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn-delete-rule'
    deleteButton.type = 'button';
    deleteButton.textContent = 'X';
    deleteButton.onclick = () => container.removeChild(ruleDiv);

    ruleDiv.appendChild(input);
    ruleDiv.appendChild(deleteButton);
    container.appendChild(ruleDiv);
}

// Display loading text
const STATUS_MSG = " model, this may take a moment... You can view current progress in the terminal. You will be redirected to the 'Manage Models' page when generation is complete.";
const form = document.getElementById('model-form');
const generatingStatus = document.getElementById('generate-model-status');
const statusText = generatingStatus.querySelector('#status-text');
form.addEventListener('submit', function(event) {
    statusText.textContent += STATUS_MSG;
    generatingStatus.style.display = 'block';
});
        
