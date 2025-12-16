document.getElementById('drop-zone').addEventListener('click', () => {
    document.getElementById('video-input').click();
});

// Show upload button when file is selected
document.getElementById('video-input').addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const btn = document.getElementById('upload-btn');
        btn.style.display = 'block';
        btn.textContent = `Clean "${file.name}"`;
    }
});

document.getElementById('upload-form').addEventListener('submit', function (e) {
    const file = document.getElementById('video-input').files[0];
    if (file && file.size > 500 * 1024 * 1024) {
        alert("File too large! Max 500MB");
        e.preventDefault();
        return;
    }
    document.getElementById('drop-zone').style.display = 'none';
    document.getElementById('progress-container').style.display = 'block';

    // Fake progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        document.getElementById('progress-fill').style.width = progress + '%';
    }, 800);
});