// Fungsi untuk verifikasi token dan navigasi halaman
async function verifyTokenLogin() {
    // Ambil token dari localStorage
    const token = localStorage.getItem('authToken');
    // Jika tidak ada token, alihkan ke login
    if (!token) return ;
    try {
        // Kirim permintaan verifikasi token
        const response = await fetch('/verify-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token  // Sertakan token dalam header
            }
        });
        // Parsing hasil JSON dari respon
        const result = await response.json();
        // Jika token valid, simpan username dan valid ke localStorage
        if (result.valid) {
            console.log('Token valid. Username:', result.username);
            // Lanjut ke halaman yang diinginkan setelah verifikasi berhasil
            window.location.href = "/dashboard"; // Ganti dengan halaman tujuan
        } else {
            // Jika token invalid, arahkan ke login
            localStorage.removeItem('authToken');
        }
    } catch (error) {
        console.error('Error verifying token:', error);
        // Arahkan ke login jika terjadi error
    }
}

async function verifyTokenSetelahLogin() {
    const token = localStorage.getItem('authToken');
    if (!token) return redirectToLogin();

    try {
        const res = await fetch('/verify-token', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Authorization': token}
        });
        const { valid, username, role } = await res.json();
        if (valid) {    
            var currentUrl = window.location.href;
            console.log(currentUrl);
            setupRoleBasedContent(role,username);
        } else {
            redirectToLogin();
        }
    } catch { redirectToLogin(); }
}

// Panggil fungsi verifikasi saat halaman dimuat
if (document.location.href ==="login" or "register" or "forgot_password"or "reset_password" or "verif_email" ){
    document.addEventListener("DOMContentLoaded", verifyTokenLogin);
}
else{
    document.addEventListener("DOMContentLoaded", verifyTokenSetelahLogin);
}
function setupRoleBasedContent(role,username) {
    const roleText = role === 'murid' ? 'Murid' : 'Guru';
    document.getElementById('role-title').textContent = roleText;
    document.getElementById('role-detail').textContent = roleText;
    document.getElementById('username').textContent = username;
    if (role === 'murid') {
        document.getElementById('link-jadwal').href = "/manage_jadwal";
        document.getElementById('link-kehadiran').href = "/daftar_hadir_ujian";
        document.getElementById('link-ujian').href = "/daftar_hadir";
        document.getElementById('nav-menu').insertAdjacentHTML('beforeend', `<a href="/menu_pembayaran"><i class="fas fa-credit-card mr-2"></i> Pembayaran</a>`);
        document.getElementById('additional-info').textContent = 'Kelas: IX IPA';
    } else {
        document.getElementById('link-jadwal').href= "/manage_jadwal";
        document.getElementById('link-kehadiran').href = "/manage_kehadiran";
        document.getElementById('link-ujian').href = "/manage_ujian";
        document.getElementById('additional-info').textContent = 'Mata Pelajaran: IPA';
    }
}

function handleLogout() {
    localStorage.clear();
    redirectToLogin();
}

function redirectToLogin() {
    window.location.href = "/login";
}
