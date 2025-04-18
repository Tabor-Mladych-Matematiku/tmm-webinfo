function togglePasswordVisibility(button) {
    const target = document.querySelector(button.getAttribute('data-target'));
    if (target) {
        if (target.type === 'password') {
            target.type = 'text';
            button.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
            target.type = 'password';
            button.innerHTML = '<i class="bi bi-eye"></i>';
        }
    }
}
