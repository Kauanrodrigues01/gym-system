// Format CPF
const cpfInput = document.getElementById('id_cpf');
cpfInput.addEventListener('input', (e) => {
  let input = e.target.value.replace(/\D/g, ''); // Remove non-numeric characters
  const formatted = input
    .replace(/^(\d{3})(\d)/, '$1.$2') // Add first dot
    .replace(/^(\d{3}\.\d{3})(\d)/, '$1.$2') // Add second dot
    .replace(/^(\d{3}\.\d{3}\.\d{3})(\d)/, '$1-$2') // Add hyphen
    .slice(0, 14); // Limit to max length
  e.target.value = formatted;
});