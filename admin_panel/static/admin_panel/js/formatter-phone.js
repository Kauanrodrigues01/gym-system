// Format Phone Number
const phoneInput = document.getElementById('student-phone');
phoneInput.addEventListener('input', (e) => {
  let input = e.target.value.replace(/\D/g, ''); // Remove non-numeric characters
  const formatted = input
    .replace(/^(\d{2})(\d)/, '($1) $2') // Format DDD
    .replace(/(\d{5})(\d{1,4})/, '$1-$2') // Add hyphen
    .slice(0, 15); // Limit to max length
  e.target.value = formatted;
});