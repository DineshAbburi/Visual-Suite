function validateForm() {
    const password = document.getElementById('password').value;
    const rePassword = document.getElementById('re_password').value;
    if (password !== rePassword) {
        document.getElementById('msg').innerText = 'Passwords do not match!';
        return false;
    }
    return true;
}