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