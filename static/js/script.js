document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll("nav .header-btn");
    const currentUrl = window.location.pathname;

    links.forEach(link => {
        const linkPath = new URL(link.href).pathname; // Obtém o caminho do link
        if (linkPath === currentUrl) {
            link.classList.add('selected');
        }
    });
});

const flashMessage = document.getElementById("flash");
if (flashMessage) {
    flashMessage.style.display = 'block'; // Mostrar a mensagem
    setTimeout(() => {
        flashMessage.style.display = 'none';
    }, 3000);
}

document.getElementById('toggleFiltros').addEventListener('click', function() {
    const formulario = document.getElementById('formFiltros');
    if (formulario.style.display === 'none' || formulario.style.display === '') {
        formulario.style.display = 'block';
        this.textContent = 'Esconder Filtros';
    } else {
        formulario.style.display = 'none'; 
        this.textContent = 'Mostrar Filtros';
    }
})

document.querySelectorAll('[id^=toggleEdit]').forEach(button => {
    button.addEventListener('click', function() {
        const taskId = this.id.split('-')[1];
        const editDiv = document.getElementById(`editTask-${taskId}`);
        if (editDiv.style.display === 'none') {
            editDiv.style.display = 'flex';
        } else {
            editDiv.style.display = 'none';
        }
    });
});

document.querySelectorAll('.closeModal').forEach(button => {
    button.addEventListener('click', function() {
        const editDiv = this.closest('div');
        editDiv.style.display = 'none';
    });
});