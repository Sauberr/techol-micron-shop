document.querySelectorAll('.js-btn-password').forEach(function(btn) {
    btn.onclick = function(e) {
        e.preventDefault();
        let inputPass = btn.previousElementSibling;
        if (inputPass.getAttribute('type') === 'password') {
            inputPass.setAttribute('type', 'text');
            btn.classList.add('active');
            btn.innerHTML = '<i class="fa-solid fa-eye"></i>'; // Open eye icon
        } else {
            inputPass.setAttribute('type', 'password');
            btn.classList.remove('active');
            btn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>'; // Closed eye icon
        }
    }
});