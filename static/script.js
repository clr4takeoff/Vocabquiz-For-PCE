document.addEventListener('DOMContentLoaded', () => {
    const resultDiv = document.querySelector('.result');
    const exampleBox = document.getElementById('example-box');

    if (resultDiv && exampleBox) {
        const example = resultDiv.getAttribute('data-example');
        if (example) {
            exampleBox.textContent = `예문: ${example}`;
        }
    }
});
