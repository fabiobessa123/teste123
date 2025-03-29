// Efeito de digitação no hero
const heroTitle = document.querySelector('.hero-text h1');
const text = "Transforme ideias em conhecimento";
let index = 0;

function typeWriter() {
    if (index < text.length) {
        heroTitle.innerHTML += text.charAt(index);
        index++;
        setTimeout(typeWriter, 100);
    }
}

// Inicia animação quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    typeWriter();
    
    // Efeito parallax
    window.addEventListener('scroll', () => {
        const scrollPosition = window.pageYOffset;
        document.querySelector('.hero-image img').style.transform = 
            `translateY(${scrollPosition * 0.3}px)`;
    });
});