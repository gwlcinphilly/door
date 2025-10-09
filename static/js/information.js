/**
 * Information table functionality for FastAPI
 * Similar to Django information_table.js but adapted for FastAPI
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing information table...');
    
    // Add a small delay to ensure all elements are fully rendered
    setTimeout(function() {
        if (typeof window.reinitializeDataTable === 'function') {
            window.reinitializeDataTable();
        }
    }, 100);
    
    // Initialize tooltips for source icons
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Check if the table exists
    const informationTable = document.getElementById('informationTable');
    if (!informationTable) {
        console.log('Information table not found, exiting...');
        return;
    }
    
    // Check if DataTables is available (you might need to include DataTables in your base template)
    if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
        console.log('DataTables is available, proceeding with initialization...');
        
        // Initialize DataTable with better error handling
        try {
            // Check if table exists and has the correct structure
            const table = $('#informationTable');
            if (table.length === 0) {
                console.log('Information table not found, skipping DataTable initialization');
                return;
            }
            
            // Count columns in the table header
            const headerCols = table.find('thead tr th').length;
            const bodyRows = table.find('tbody tr').length;
            console.log(`Table structure: ${headerCols} columns, ${bodyRows} rows`);
            
            // Only initialize if we have the expected column count
            if (headerCols !== 5) {
                console.error(`Expected 5 columns, found ${headerCols}. Skipping DataTable initialization.`);
                console.log('Table header HTML:', table.find('thead')[0]?.outerHTML);
                return;
            }
            
            // Check if we have a "no data" row with colspan
            const noDataRow = table.find('tbody tr td[colspan]');
            if (noDataRow.length > 0) {
                console.log('Found no-data row with colspan, this should work fine with DataTables');
            }
            
            // Destroy existing DataTable if it exists
            if ($.fn.DataTable.isDataTable('#informationTable')) {
                $('#informationTable').DataTable().destroy();
            }
            
            window.informationDataTable = $('#informationTable').DataTable({
                responsive: true,
                pageLength: 10,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                order: [[0, 'desc']], // Sort by Date descending (newest entries first)
                columnDefs: [
                    { targets: 3, orderable: false, searchable: false }, // Actions column
                    { targets: 4, orderable: false, searchable: false }  // Comments column
                ],
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                     '<"row"<"col-sm-12"tr>>' +
                     '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                language: {
                    emptyTable: "No information available"
                }
            });
            console.log('DataTable initialized successfully');
        } catch (e) {
            console.error('Error initializing DataTable:', e);
            console.error('Table HTML:', $('#informationTable')[0]?.outerHTML);
        }
    } else {
        console.log('DataTables not available, using basic table functionality');
    }
    
    // Function to reinitialize DataTables (useful for page refreshes)
    window.reinitializeDataTable = function() {
        if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
            const table = $('#informationTable');
            if (table.length > 0 && !$.fn.DataTable.isDataTable('#informationTable')) {
                console.log('Reinitializing DataTable...');
                try {
                    window.informationDataTable = table.DataTable({
                        responsive: true,
                        pageLength: 10,
                        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                        order: [[0, 'desc']],
                        columnDefs: [
                            { targets: 3, orderable: false, searchable: false },
                            { targets: 4, orderable: false, searchable: false }
                        ],
                        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                             '<"row"<"col-sm-12"tr>>' +
                             '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                        language: {
                            emptyTable: "No information available"
                        }
                    });
                    console.log('DataTable reinitialized successfully');
                } catch (e) {
                    console.error('Error reinitializing DataTable:', e);
                }
            }
        }
    };
    
    // Handle No Tag filter checkbox
    const noTagFilter = document.getElementById('noTagFilter');
    if (noTagFilter) {
        noTagFilter.addEventListener('change', function() {
            const url = new URL(window.location);
            if (this.checked) {
                url.searchParams.set('no_tag', '1');
                // Disable other tag checkboxes when No Tag is selected
                disableOtherTagCheckboxes(true);
            } else {
                url.searchParams.delete('no_tag');
                // Re-enable other tag checkboxes when No Tag is unchecked
                disableOtherTagCheckboxes(false);
            }
            window.location.href = url.toString();
        });
    }
    
    // Handle Check Tag filter checkbox
    const checkTagFilter = document.getElementById('checkTagFilter');
    if (checkTagFilter) {
        checkTagFilter.addEventListener('change', function() {
            const url = new URL(window.location);
            if (this.checked) {
                url.searchParams.set('check_tag', '1');
                // Disable No Tag checkbox when any other tag is selected
                disableNoTagCheckbox(true);
            } else {
                url.searchParams.delete('check_tag');
                // Re-enable No Tag checkbox when other tags are unchecked
                disableNoTagCheckbox(false);
            }
            window.location.href = url.toString();
        });
    }
    
    // Function to disable/enable other tag checkboxes
    function disableOtherTagCheckboxes(disable) {
        const checkTagFilter = document.getElementById('checkTagFilter');
        if (checkTagFilter) {
            checkTagFilter.disabled = disable;
            if (disable) {
                checkTagFilter.classList.add('text-muted');
                checkTagFilter.closest('.form-check').classList.add('text-muted');
            } else {
                checkTagFilter.classList.remove('text-muted');
                checkTagFilter.closest('.form-check').classList.remove('text-muted');
            }
        }
        // Add more tag checkboxes here as they are implemented
    }
    
    // Function to disable/enable No Tag checkbox
    function disableNoTagCheckbox(disable) {
        const noTagFilter = document.getElementById('noTagFilter');
        if (noTagFilter) {
            noTagFilter.disabled = disable;
            if (disable) {
                noTagFilter.classList.add('text-muted');
                noTagFilter.closest('.form-check').classList.add('text-muted');
            } else {
                noTagFilter.classList.remove('text-muted');
                noTagFilter.closest('.form-check').classList.remove('text-muted');
            }
        }
    }
    
    // Initialize checkbox states on page load
    function initializeCheckboxStates() {
        const noTagFilter = document.getElementById('noTagFilter');
        const checkTagFilter = document.getElementById('checkTagFilter');
        
        if (noTagFilter && checkTagFilter) {
            // If No Tag is checked, disable other checkboxes
            if (noTagFilter.checked) {
                disableOtherTagCheckboxes(true);
            }
            
            // If any other tag is checked, disable No Tag checkbox
            if (checkTagFilter.checked) {
                disableNoTagCheckbox(true);
            }
        }
    }
    
    // Initialize checkbox states when page loads
    initializeCheckboxStates();
    
    // Initialize tag selection functionality
    initializeTagSelection();
    
    // Handle edit information form submission
    const editInfoForm = document.getElementById('editInfoForm');
    if (editInfoForm) {
        editInfoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitEditInfoForm();
        });
    }
    
    // Handle edit information modal using event delegation for dynamic content
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-info-btn') || e.target.closest('.edit-info-btn')) {
            const button = e.target.classList.contains('edit-info-btn') ? e.target : e.target.closest('.edit-info-btn');
            
            const infoId = button.getAttribute('data-id');
            const infoUrl = button.getAttribute('data-url');
            const infoSourceId = button.getAttribute('data-source-id');
            const infoSourceShort = button.getAttribute('data-source-short');
            const infoTags = button.getAttribute('data-tags');
            const infoTitle = button.getAttribute('data-title');
            const infoContent = button.getAttribute('data-content');
            
            console.log('Edit button clicked for entry:', infoId);
            console.log('Source ID:', infoSourceId, 'Source Short:', infoSourceShort);
            
            // Populate edit modal fields
            document.getElementById('edit_info_id').value = infoId;
            document.getElementById('edit_url').value = infoUrl;
            document.getElementById('edit_title').value = infoTitle;
            document.getElementById('edit_content').value = infoContent;
            
            // Store current info ID for delete and refresh operations
            document.getElementById('deleteInfoBtn').setAttribute('data-info-id', infoId);
            document.getElementById('checkAgainBtn').setAttribute('data-info-id', infoId);
            
            // Load and display current tags for this entry
            loadEntryTags(parseInt(infoId));
            
            // Handle source selection
            const sourceSelect = document.getElementById('edit_source');
            if (sourceSelect && infoSourceId) {
                sourceSelect.value = infoSourceId;
            }
        }
    });
    
    // Handle delete button in edit modal
    const deleteInfoBtn = document.getElementById('deleteInfoBtn');
    if (deleteInfoBtn) {
        deleteInfoBtn.addEventListener('click', function() {
            const infoId = this.getAttribute('data-info-id');
            if (infoId && confirm('Are you sure you want to delete this information entry? This action cannot be undone.')) {
                deleteInfoFromModal(parseInt(infoId));
            }
        });
    }
    
    // Handle check again button in edit modal
    const checkAgainBtn = document.getElementById('checkAgainBtn');
    if (checkAgainBtn) {
        checkAgainBtn.addEventListener('click', function() {
            const infoId = this.getAttribute('data-info-id');
            if (infoId) {
                refreshMetadataFromModal(parseInt(infoId));
            }
        });
    }
    
    // Handle delete information using event delegation for dynamic content
    document.addEventListener('click', function(e) {
        if (e.target.matches('[onclick*="deleteInfo"]')) {
            e.preventDefault();
            const infoId = e.target.getAttribute('onclick').match(/\d+/)[0];
            deleteInfo(parseInt(infoId));
        }
    });
    
    // Handle Update All Documents button
    const updateAllBtn = document.getElementById('updateAllBtn');
    if (updateAllBtn) {
        updateAllBtn.addEventListener('click', async function() {
            if (confirm('Are you sure you want to update all documents? This may take some time.')) {
                try {
                    // Show loading state
                    updateAllBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Updating...';
                    updateAllBtn.disabled = true;
                    
                    // Make API call to update all documents
                    const response = await fetch('/information/api/update-all', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    
                    if (response.ok) {
                        alert('All documents updated successfully!');
                        location.reload();
                    } else {
                        const error = await response.json();
                        alert('Error: ' + (error.detail || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error updating documents: ' + error.message);
                } finally {
                    // Reset button
                    updateAllBtn.innerHTML = '<i class="bi bi-arrow-repeat"></i> Update All Documents';
                    updateAllBtn.disabled = false;
                }
            }
        });
    }
    
    // Initialize InfoSource modal functionality
    initializeInfoSourceModal();
    
    // Initialize InfoTag modal functionality
    initializeInfoTagModal();
    
    console.log('Information table initialization complete');
});

// Initialize InfoSource modal functionality
function initializeInfoSourceModal() {
    console.log('Initializing InfoSource modal functionality...');
    
    // Handle clicking on existing source buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-source-btn')) {
            e.preventDefault();
            console.log('Source button clicked!');
            
            const sourceId = e.target.getAttribute('data-source-id');
            const sourceShort = e.target.getAttribute('data-source-short');
            const sourceName = e.target.getAttribute('data-source-name');
            const sourceDescription = e.target.getAttribute('data-source-description');
            
            console.log('Source data:', {
                id: sourceId,
                short: sourceShort,
                name: sourceName,
                description: sourceDescription
            });
            
            // Populate the form with existing source data
            document.getElementById('info_source_id').value = sourceId;
            document.getElementById('info_source_short').value = sourceShort;
            document.getElementById('info_source_name').value = sourceName;
            document.getElementById('info_source_description').value = sourceDescription;
            
            // Update modal title and button text
            document.getElementById('addInfoSourceModalLabel').textContent = 'Edit Info Source';
            document.getElementById('submitSourceBtn').textContent = 'Update Source';
            
            // Highlight the clicked button
            document.querySelectorAll('.edit-source-btn').forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-secondary');
            });
            e.target.classList.remove('btn-outline-secondary');
            e.target.classList.add('btn-primary');
        }
    });
    
    // Handle clear form button
    const clearSourceForm = document.getElementById('clearSourceForm');
    if (clearSourceForm) {
        clearSourceForm.addEventListener('click', clearSourceFormFields);
    }
    
    // Handle modal show event to reset form for new sources
    const addInfoSourceModal = document.getElementById('addInfoSourceModal');
    if (addInfoSourceModal) {
        addInfoSourceModal.addEventListener('show.bs.modal', function() {
            // Only clear if we're not editing an existing source
            if (!document.getElementById('info_source_id').value) {
                clearSourceFormFields();
            }
        });
        
        // Handle modal hidden event to reset everything
        addInfoSourceModal.addEventListener('hidden.bs.modal', function() {
            clearSourceFormFields();
        });
    }
    
    // Handle form submission
    const addInfoSourceForm = document.getElementById('addInfoSourceForm');
    if (addInfoSourceForm) {
        addInfoSourceForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/information/api/sources', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Source saved successfully!');
                    location.reload();
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.detail);
                }
            } catch (error) {
                alert('Error saving source: ' + error.message);
            }
        });
    }
    
    // Function to clear the source form
    function clearSourceFormFields() {
        document.getElementById('info_source_id').value = '';
        document.getElementById('info_source_short').value = '';
        document.getElementById('info_source_name').value = '';
        document.getElementById('info_source_description').value = '';
        
        // Reset modal title and button text
        document.getElementById('addInfoSourceModalLabel').textContent = 'Add Info Source';
        document.getElementById('submitSourceBtn').textContent = 'Add Source';
        
        // Reset button styles
        document.querySelectorAll('.edit-source-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-secondary');
        });
        
        console.log('Source form cleared');
    }
    
    console.log('InfoSource modal functionality initialized');
}

// Initialize InfoTag modal functionality
function initializeInfoTagModal() {
    console.log('Initializing InfoTag modal functionality...');
    
    // Handle clicking on existing tag buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-tag-btn')) {
            e.preventDefault();
            console.log('Tag button clicked!');
            
            const tagId = e.target.getAttribute('data-tag-id');
            const tagCode = e.target.getAttribute('data-tag-code');
            const tagName = e.target.getAttribute('data-tag-name');
            const tagDescription = e.target.getAttribute('data-tag-description');
            
            console.log('Tag data:', {
                id: tagId,
                code: tagCode,
                name: tagName,
                description: tagDescription
            });
            
            // Populate the form with existing tag data
            document.getElementById('info_tag_id').value = tagId;
            document.getElementById('info_tag_tag').value = tagCode;
            document.getElementById('info_tag_name').value = tagName;
            document.getElementById('info_tag_description').value = tagDescription;
            
            // Update modal title and button text
            document.getElementById('addInfoTagModalLabel').textContent = 'Edit Info Tag';
            document.getElementById('submitTagBtn').textContent = 'Update Tag';
            
            // Highlight the clicked button
            document.querySelectorAll('.edit-tag-btn').forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-secondary');
            });
            e.target.classList.remove('btn-outline-secondary');
            e.target.classList.add('btn-primary');
        }
    });
    
    // Handle clear form button
    const clearTagForm = document.getElementById('clearTagForm');
    if (clearTagForm) {
        clearTagForm.addEventListener('click', clearTagFormFields);
    }
    
    // Handle modal show event to reset form for new tags
    const addInfoTagModal = document.getElementById('addInfoTagModal');
    if (addInfoTagModal) {
        addInfoTagModal.addEventListener('show.bs.modal', function() {
            // Only clear if we're not editing an existing tag
            if (!document.getElementById('info_tag_id').value) {
                clearTagFormFields();
            }
        });
        
        // Handle modal hidden event to reset everything
        addInfoTagModal.addEventListener('hidden.bs.modal', function() {
            clearTagFormFields();
        });
    }
    
    // Handle form submission
    const addInfoTagForm = document.getElementById('addInfoTagForm');
    if (addInfoTagForm) {
        addInfoTagForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/information/api/tags', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Tag saved successfully!');
                    location.reload();
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.detail);
                }
            } catch (error) {
                alert('Error saving tag: ' + error.message);
            }
        });
    }
    
    // Function to clear the tag form
    function clearTagFormFields() {
        document.getElementById('info_tag_id').value = '';
        document.getElementById('info_tag_tag').value = '';
        document.getElementById('info_tag_name').value = '';
        document.getElementById('info_tag_description').value = '';
        
        // Reset modal title and button text
        document.getElementById('addInfoTagModalLabel').textContent = 'Add Info Tag';
        document.getElementById('submitTagBtn').textContent = 'Add Tag';
        
        // Reset button styles
        document.querySelectorAll('.edit-tag-btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-secondary');
        });
        
        console.log('Tag form cleared');
    }
    
    console.log('InfoTag modal functionality initialized');
}

// Delete information function
async function deleteInfo(infoId) {
    if (confirm('Are you sure you want to delete this information entry?')) {
        try {
            const response = await fetch(`/information/api/information/${infoId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Information entry deleted successfully!');
                location.reload();
            } else {
                const error = await response.json();
                alert('Error: ' + error.detail);
            }
        } catch (error) {
            alert('Error deleting information: ' + error.message);
        }
    }
}

// Delete information from modal function
async function deleteInfoFromModal(infoId) {
    try {
        const response = await fetch(`/information/api/information/${infoId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Information entry deleted successfully!');
            // Close the modal and reload the page
            const modal = bootstrap.Modal.getInstance(document.getElementById('editInfoModal'));
            if (modal) {
                modal.hide();
            }
            location.reload();
        } else {
            const error = await response.json();
            alert('Error: ' + error.detail);
        }
    } catch (error) {
        alert('Error deleting information: ' + error.message);
    }
}

// Refresh metadata from modal function
async function refreshMetadataFromModal(infoId) {
    try {
        // Show loading state on the button
        const checkAgainBtn = document.getElementById('checkAgainBtn');
        const originalText = checkAgainBtn.innerHTML;
        checkAgainBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Checking...';
        checkAgainBtn.disabled = true;
        
        const response = await fetch(`/information/api/information/${infoId}/refresh`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Update the modal fields with refreshed data
            document.getElementById('edit_title').value = result.information.title;
            document.getElementById('edit_content').value = result.information.content;
            
            // Metadata refreshed successfully - no alert needed, form is updated
        } else {
            const error = await response.json();
            alert('Error refreshing metadata: ' + error.detail);
        }
    } catch (error) {
        alert('Error refreshing metadata: ' + error.message);
    } finally {
        // Reset button state
        const checkAgainBtn = document.getElementById('checkAgainBtn');
        checkAgainBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Check Again';
        checkAgainBtn.disabled = false;
    }
}

// Initialize tag selection functionality
function initializeTagSelection() {
    console.log('Initializing tag selection functionality...');
    
    // Handle tag button clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tag-select-btn')) {
            e.preventDefault();
            toggleTagSelection(e.target);
        }
        
        // Handle remove tag button clicks
        if (e.target.classList.contains('remove-tag-btn')) {
            e.preventDefault();
            removeTag(e.target);
        }
    });
    
    // Initialize tag search functionality
    initializeTagSearch();
}

// Initialize tag search functionality
function initializeTagSearch() {
    const searchInput = document.getElementById('edit_tag_search');
    const clearSearchBtn = document.getElementById('edit_clear_search');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTags(this.value);
        });
    }
    
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            document.getElementById('edit_tag_search').value = '';
            filterTags('');
        });
    }
}

// Filter tags based on search input
function filterTags(searchTerm) {
    const tagButtons = document.querySelectorAll('.tag-select-btn');
    const noMatchingMessage = document.getElementById('edit_no_matching_tags');
    let visibleCount = 0;
    
    const searchLower = searchTerm.toLowerCase().trim();
    
    tagButtons.forEach(button => {
        const tagName = button.getAttribute('data-tag-name').toLowerCase();
        const tagCode = button.getAttribute('data-tag-code').toLowerCase();
        
        if (searchLower === '' || tagName.includes(searchLower) || tagCode.includes(searchLower)) {
            button.style.display = 'inline-block';
            visibleCount++;
        } else {
            button.style.display = 'none';
        }
    });
    
    // Show/hide "no matching tags" message
    if (visibleCount === 0 && searchLower !== '') {
        noMatchingMessage.style.display = 'block';
    } else {
        noMatchingMessage.style.display = 'none';
    }
    
    // Update available count
    const availableCount = document.getElementById('edit_available_count');
    if (availableCount) {
        availableCount.textContent = `${visibleCount} available`;
    }
}

// Toggle tag selection
function toggleTagSelection(tagButton) {
    const tagId = tagButton.getAttribute('data-tag-id');
    const tagName = tagButton.getAttribute('data-tag-name');
    const tagCode = tagButton.getAttribute('data-tag-code');
    
    // Check if tag is already selected
    const selectedTagIds = getSelectedTagIds();
    
    if (selectedTagIds.includes(tagId)) {
        // Tag is selected, remove it
        removeTagFromSelection(tagId);
        tagButton.classList.remove('btn-primary');
        tagButton.classList.add('btn-outline-secondary');
    } else {
        // Tag is not selected, add it
        addTagToSelection(tagId, tagName, tagCode);
        tagButton.classList.remove('btn-outline-secondary');
        tagButton.classList.add('btn-primary');
    }
}

// Add tag to selection
function addTagToSelection(tagId, tagName, tagCode) {
    const selectedTagsContainer = document.getElementById('edit_selected_tags');
    const noTagsMessage = document.getElementById('edit_no_tags_message');
    console.log('DEBUG: addTagToSelection - adding tag:', tagName, 'container children before:', selectedTagsContainer.children.length);
    
    // Hide "no tags" message if it exists
    if (noTagsMessage) {
        noTagsMessage.style.display = 'none';
    }
    
    // Add flexbox classes when we have content
    if (selectedTagsContainer.children.length === 0) {
        selectedTagsContainer.className = 'd-flex flex-wrap gap-2';
    }
    
    const tagElement = document.createElement('div');
    tagElement.className = 'badge bg-primary me-1 mb-1 d-flex align-items-center';
    tagElement.setAttribute('data-tag-id', tagId);
    tagElement.innerHTML = `
        <i class="bi bi-tag-fill me-1"></i>
        ${tagName}
        <button type="button" class="btn-close btn-close-white ms-1 remove-tag-btn" 
                data-tag-id="${tagId}" aria-label="Remove ${tagName}" style="font-size: 0.7em;"></button>
    `;
    selectedTagsContainer.appendChild(tagElement);
    
    console.log('DEBUG: addTagToSelection - container children after:', selectedTagsContainer.children.length);
    updateSelectedTagIds();
    updateTagCount();
}

// Remove tag from selection
function removeTagFromSelection(tagId) {
    // Remove from selected tags display
    const selectedTagsContainer = document.getElementById('edit_selected_tags');
    const noTagsMessage = document.getElementById('edit_no_tags_message');
    const tagElements = selectedTagsContainer.querySelectorAll(`[data-tag-id="${tagId}"]`);
    tagElements.forEach(el => el.closest('.badge').remove());
    
    // Show "no tags" message if container becomes empty
    if (selectedTagsContainer.children.length === 0) {
        selectedTagsContainer.className = '';
        if (noTagsMessage) {
            noTagsMessage.style.display = 'block';
        }
    }
    
    // Update button appearance
    const tagButton = document.querySelector(`.tag-select-btn[data-tag-id="${tagId}"]`);
    if (tagButton) {
        tagButton.classList.remove('btn-primary');
        tagButton.classList.add('btn-outline-secondary');
    }
    
    updateSelectedTagIds();
    updateTagCount();
}

// Remove tag when clicking remove button
function removeTag(removeButton) {
    const tagId = removeButton.getAttribute('data-tag-id');
    removeTagFromSelection(tagId);
}

// Get currently selected tag IDs
function getSelectedTagIds() {
    const hiddenInput = document.getElementById('edit_selected_tag_ids');
    const value = hiddenInput.value;
    return value ? value.split(',').filter(id => id.trim()) : [];
}

// Update hidden input with selected tag IDs
function updateSelectedTagIds() {
    const selectedTagsContainer = document.getElementById('edit_selected_tags');
    const tagElements = selectedTagsContainer.querySelectorAll('.badge[data-tag-id]');
    const tagIds = Array.from(tagElements).map(el => el.getAttribute('data-tag-id'));
    
    console.log('DEBUG: updateSelectedTagIds - found elements:', tagElements.length);
    console.log('DEBUG: updateSelectedTagIds - tagIds:', tagIds);
    
    const hiddenInput = document.getElementById('edit_selected_tag_ids');
    hiddenInput.value = tagIds.join(',');
    
    console.log('DEBUG: updateSelectedTagIds - hidden input value:', hiddenInput.value);
}

// Update tag count display
function updateTagCount() {
    const selectedTags = document.querySelectorAll('#edit_selected_tags .badge');
    const countBadge = document.getElementById('edit_tag_count');
    
    if (countBadge) {
        const count = selectedTags.length;
        countBadge.textContent = `${count} selected`;
        
        // Update badge color based on count
        if (count === 0) {
            countBadge.className = 'badge bg-secondary ms-2';
        } else {
            countBadge.className = 'badge bg-primary ms-2';
        }
    }
}

// Load tags for a specific entry
async function loadEntryTags(infoId) {
    try {
        const response = await fetch(`/information/api/information/${infoId}`);
        if (response.ok) {
            const info = await response.json();
            console.log('DEBUG: loadEntryTags - loaded info:', info);
            console.log('DEBUG: loadEntryTags - tags from API:', info.tags);
            
            // Clear current selection
            const selectedTagsContainer = document.getElementById('edit_selected_tags');
            const noTagsMessage = document.getElementById('edit_no_tags_message');
            console.log('DEBUG: loadEntryTags - clearing container, current children:', selectedTagsContainer.children.length);
            
            selectedTagsContainer.innerHTML = '';
            selectedTagsContainer.className = ''; // Remove any flexbox classes
            document.getElementById('edit_selected_tag_ids').value = '';
            
            // Show "no tags" message initially
            if (noTagsMessage) {
                noTagsMessage.style.display = 'block';
            }
            
            console.log('DEBUG: loadEntryTags - after clearing, children:', selectedTagsContainer.children.length);
            
            // Reset all tag buttons to unselected state
            document.querySelectorAll('.tag-select-btn').forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-secondary');
            });
            
            // Add tags from the entry
            if (info.tags && info.tags.length > 0) {
                console.log(`DEBUG: loadEntryTags - adding ${info.tags.length} tags:`, info.tags);
                info.tags.forEach(tag => {
                    console.log('DEBUG: loadEntryTags - adding tag:', tag);
                    addTagToSelection(tag.id, tag.name, tag.tag);
                });
            } else {
                console.log('DEBUG: loadEntryTags - no tags to add');
            }
            
            // Clear search and reset filter
            const searchInput = document.getElementById('edit_tag_search');
            if (searchInput) {
                searchInput.value = '';
                filterTags('');
            }
            
            updateTagCount();
        } else {
            console.error('Failed to load entry tags');
        }
    } catch (error) {
        console.error('Error loading entry tags:', error);
    }
}

// Submit edit information form
async function submitEditInfoForm() {
    try {
        const formData = new FormData(document.getElementById('editInfoForm'));
        const data = Object.fromEntries(formData.entries());
        
        // Debug: Log the form data to see what's being sent
        console.log('Form data being sent:', data);
        
        const infoId = data.id;
        if (!infoId) {
            alert('Error: No information ID found');
            return;
        }
        
        // Show loading state
        const submitBtn = document.querySelector('#editInfoForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Updating...';
        submitBtn.disabled = true;
        
        const response = await fetch(`/information/api/information/${infoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            // Close modal and reload page
            const modal = bootstrap.Modal.getInstance(document.getElementById('editInfoModal'));
            if (modal) {
                modal.hide();
            }
            location.reload();
        } else {
            const error = await response.json();
            alert('Error updating information: ' + error.detail);
        }
    } catch (error) {
        alert('Error updating information: ' + error.message);
    } finally {
        // Reset button state
        const submitBtn = document.querySelector('#editInfoForm button[type="submit"]');
        submitBtn.innerHTML = 'Update Information';
        submitBtn.disabled = false;
    }
}

// View information function
async function viewInfo(infoId) {
    try {
        const response = await fetch(`/information/api/information/${infoId}`);
        const info = await response.json();
        
        const content = `
            <h6>Title</h6>
            <p>${info.title || 'No title'}</p>
            
            <h6>URL</h6>
            <p><a href="${info.url}" target="_blank">${info.url}</a></p>
            
            <h6>Content</h6>
            <p>${info.content || 'No content'}</p>
            
            <h6>Date Added</h6>
            <p>${new Date(info.date).toLocaleString()}</p>
            
            <h6>Last Updated</h6>
            <p>${new Date(info.updated_at).toLocaleString()}</p>
        `;
        
        document.getElementById('viewInfoContent').innerHTML = content;
        new bootstrap.Modal(document.getElementById('viewInfoModal')).show();
    } catch (error) {
        alert('Error loading information: ' + error.message);
    }
}

// Edit information function
async function editInfo(infoId) {
    try {
        const response = await fetch(`/information/api/information/${infoId}`);
        const info = await response.json();
        
        document.getElementById('edit_info_id').value = info.id;
        document.getElementById('edit_url').value = info.url;
        document.getElementById('edit_title').value = info.title || '';
        document.getElementById('edit_content').value = info.content || '';
        
        new bootstrap.Modal(document.getElementById('editInfoModal')).show();
    } catch (error) {
        alert('Error loading information: ' + error.message);
    }
}
