const form = document.getElementById('spellcheck-form');
const fileInput = document.getElementById('file-input');
const textInput = document.getElementById('text-input');
const correctedOutput = document.getElementById('corrected-output');
const downloadBtn = document.getElementById('download-btn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    correctedOutput.innerHTML = 'Checking... This may take a few seconds, we appreciate your patience.';
    downloadBtn.classList.add('d-none');

    // progress bar
    const progressHtml = `
        <div class="progress mb-3">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" style="width: 25%">Processing...</div>
        </div>
    `;
    correctedOutput.innerHTML = progressHtml + correctedOutput.innerHTML;

    const model = document.getElementById('model-select').value;
    let response;

    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('model_type', model);

        response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
    } else {
        response = await fetch('/api/spellcheck', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: textInput.value,
                model_type: model
            })
        });
    }

    const data = await response.json();
    if (data.corrected_text) {
        correctedOutput.innerHTML = highlightErrors(data.corrected_text, data.errors);
        activatePopovers();

        if (data.statistics) {
            displayStatistics(data.statistics, data.errors);
        }

        const blob = new Blob([data.corrected_text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        downloadBtn.href = url;
        downloadBtn.classList.remove('d-none');
    } else {
        correctedOutput.innerText = 'Error processing text.';
    }
});

function highlightErrors(correctedText, errors) {
    const tokens = correctedText.split(/\s+/);
    const highlighted = tokens.map((token, idx) => {
        const err = errors?.find(e => e.position === idx);
        if (!err) return token;

        const suggestionsHTML = err.suggestions.map(s =>
            `${s.word} [${(s.score * 100).toFixed(1)}%]`
        ).join('<br>');

        return `
      <span class="highlight" 
            data-bs-toggle="popover" 
            data-bs-html="true" 
            data-bs-content="${suggestionsHTML}"
            title="Suggestions for '${err.original}'"
      >${token}</span>`;
    });

    return highlighted.join(' ');
}

function activatePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));

    popoverTriggerList.forEach(element => {
        // Create popover with manual trigger
        const popover = new bootstrap.Popover(element, {
            trigger: 'manual',
            placement: 'top',
            html: true,
            container: 'body'
        });

        let clickLocked = false;
        let hoverTimer = null;

        // Show on hover with delay
        element.addEventListener('mouseenter', function () {
            if (!clickLocked) {
                hoverTimer = setTimeout(() => {
                    popover.show();
                }, 500);
            }
        });

        // Hide on mouse leave (unless click-locked)
        element.addEventListener('mouseleave', function () {
            clearTimeout(hoverTimer);
            if (!clickLocked) {
                popover.hide();
            }
        });

        // Toggle lock on click
        element.addEventListener('click', function (e) {
            e.stopPropagation();
            if (clickLocked) {
                clickLocked = false;
                element.classList.remove('popover-locked');
                popover.hide();
            } else {
                clickLocked = true;
                element.classList.add('popover-locked');
                clearTimeout(hoverTimer);
                popover.show();
            }
        });

        // Add click-away listener
        document.addEventListener('click', function (e) {
            if (clickLocked && !element.contains(e.target)) {
                clickLocked = false;
                element.classList.remove('popover-locked');
                popover.hide();
            }
        });
    });
}

function displayStatistics(stats, errors) {
    const statsSection = document.getElementById('statistics-section');
    const errorSummary = document.getElementById('error-summary');
    const errorTypes = document.getElementById('error-types');

    if (stats.total_errors > 0) {
        statsSection.classList.remove('d-none');

        errorSummary.innerHTML = `
            <p><strong>Total Errors Found:</strong> ${stats.total_errors}</p>
            <p><strong>Average Confidence:</strong> ${(stats.average_confidence * 100).toFixed(1)}%</p>
            <p><strong>Medical Terms Corrected:</strong> ${stats.medical_corrections} 
               (${(stats.medical_correction_rate * 100).toFixed(1)}%)</p>
        `;

        let errorTypesHtml = '<ul class="list-unstyled">';
        for (const [type, count] of Object.entries(stats.error_types || {})) {
            errorTypesHtml += `<li><strong>${type}:</strong> ${count}</li>`;
        }
        errorTypesHtml += '</ul>';
        errorTypes.innerHTML = errorTypesHtml;
    } else {
        statsSection.classList.add('d-none');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    activatePopovers();
});

const batchProcessBtn = document.getElementById('batch-process-btn');
const batchFiles = document.getElementById('batch-files');
const batchProgress = document.getElementById('batch-progress');
const batchResults = document.getElementById('batch-results');
const progressBar = batchProgress.querySelector('.progress-bar');
const currentFileSpan = document.getElementById('current-file');

batchProcessBtn.addEventListener('click', async () => {
    const files = batchFiles.files;
    if (files.length === 0) {
        alert('Please select files to process');
        return;
    }

    batchProgress.classList.remove('d-none');
    batchResults.innerHTML = '';

    const model = document.getElementById('model-select').value;
    const results = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length * 100).toFixed(0);

        progressBar.style.width = progress + '%';
        progressBar.textContent = progress + '%';
        currentFileSpan.textContent = file.name;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('model_type', model);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            results.push({
                filename: file.name,
                success: true,
                errors: data.errors ? data.errors.length : 0,
                statistics: data.statistics
            });

            if (data.corrected_text) {
                const blob = new Blob([data.corrected_text], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'corrected_' + file.name;
                link.textContent = 'Download';
                link.className = 'btn btn-sm btn-success ms-2';

                results[results.length - 1].downloadLink = link;
            }
        } catch (error) {
            results.push({
                filename: file.name,
                success: false,
                error: error.message
            });
        }
    }

    batchProgress.classList.add('d-none');

    displayBatchResults(results);
});

function displayBatchResults(results) {
    let html = '<h5>Batch Processing Results:</h5>';
    html += '<table class="table table-striped">';
    html += '<thead><tr><th>File</th><th>Status</th><th>Errors Found</th><th>Actions</th></tr></thead>';
    html += '<tbody>';

    for (const result of results) {
        html += '<tr>';
        html += `<td>${result.filename}</td>`;
        html += `<td>${result.success ? '✅ Success' : '❌ Failed'}</td>`;
        html += `<td>${result.errors || '-'}</td>`;
        html += '<td id="download-' + result.filename.replace(/\./g, '-') + '"></td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    batchResults.innerHTML = html;

    for (const result of results) {
        if (result.downloadLink) {
            const td = document.getElementById('download-' + result.filename.replace(/\./g, '-'));
            if (td) {
                td.appendChild(result.downloadLink);
            }
        }
    }
} 