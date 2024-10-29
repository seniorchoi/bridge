document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('description-form');
    const codeBlocksContainer = document.getElementById('code-blocks');
    let draggedItem = null;
    let executionOutput = '';

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const description = document.getElementById('description').value;

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'description=' + encodeURIComponent(description),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error);
                });
            }
            return response.json();
        })
        .then(data => {
            displayCodeBlocks(data.code_blocks);
            updateCodeOrder();
        })
        .catch(error => console.error('Error:', error));
    });

    function displayCodeBlocks(codeBlocks) {
        codeBlocksContainer.innerHTML = ''; // Clear previous blocks

        codeBlocks.forEach((block, index) => {
            const codeBlock = document.createElement('div');
            codeBlock.className = 'code-block';
            codeBlock.draggable = true;
            codeBlock.dataset.index = index;

            const front = document.createElement('div');
            front.className = 'front';
            front.textContent = block.title;

            const back = document.createElement('div');
            back.className = 'back';
            back.innerHTML = `<pre><code>${escapeHtml(block.code)}</code></pre>`;


            codeBlock.appendChild(front);
            codeBlock.appendChild(back);

            // Flip functionality
            codeBlock.addEventListener('click', function() {
                codeBlock.classList.toggle('flipped');
            });

            // Drag events
            codeBlock.addEventListener('dragstart', function() {
                draggedItem = codeBlock;
                setTimeout(() => {
                    codeBlock.classList.add('dragging');
                }, 0);
            });

            codeBlock.addEventListener('dragend', function() {
                codeBlock.classList.remove('dragging');
                draggedItem = null;
                updateCodeOrder();
            });

            codeBlocksContainer.appendChild(codeBlock);


            // Capture the execution output
            if (block.title === 'Execution Output') {
                executionOutput = block.code;
            }
        });

        codeBlocksContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            const afterElement = getDragAfterElement(e.clientY);
            if (afterElement == null) {
                codeBlocksContainer.appendChild(draggedItem);
            } else {
                codeBlocksContainer.insertBefore(draggedItem, afterElement);
            }
            
        });

        updateCodeOrder();
    }

    // Function to escape HTML special characters
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
            '\n': '<br>',
        };
        return text.replace(/[&<>"'\n]/g, function(m) { return map[m]; });
    }

    function getDragAfterElement(y) {
        const draggableElements = [...codeBlocksContainer.querySelectorAll('.code-block:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    function updateCodeOrder() {
        
        document.getElementById('preview-frame').srcdoc = executionOutput;
    }

});
