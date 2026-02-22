// Streamify - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize play buttons
    initPlayButtons();
    
    // Auto-dismiss alerts
    setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-info):not(.alert-warning)').forEach(el => {
            const bsAlert = new bootstrap.Alert(el);
            bsAlert.close();
        });
    }, 5000);
});

// ==================== Music Player ====================

const player = {
    audio: null,
    currentTitle: '',
    currentArtist: '',
    currentThumb: '',
    isPlaying: false,
};

function initPlayButtons() {
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const src = this.dataset.src;
            const title = this.dataset.title;
            const artist = this.dataset.artist;
            const thumb = this.dataset.thumb;
            if (src) {
                playTrack(src, title, artist, thumb);
            }
        });
    });
}

function playTrack(src, title, artist, thumb) {
    const playerEl = document.getElementById('music-player');
    const audioEl = document.getElementById('audio-element');
    
    if (!audioEl) return;
    
    audioEl.src = src;
    document.getElementById('player-title').textContent = title || 'Unknown Title';
    document.getElementById('player-artist').textContent = artist || 'Unknown Artist';
    
    const thumbEl = document.getElementById('player-thumb');
    if (thumb) {
        thumbEl.src = thumb;
        thumbEl.style.display = '';
    } else {
        thumbEl.style.display = 'none';
    }
    
    playerEl.classList.remove('d-none');
    audioEl.play().then(() => {
        player.isPlaying = true;
        document.getElementById('play-icon').className = 'bi bi-pause-fill';
    }).catch(err => console.log('Playback failed:', err));
    
    // Time update
    audioEl.addEventListener('timeupdate', updateProgress);
    audioEl.addEventListener('ended', onTrackEnded);
}

function togglePlay() {
    const audioEl = document.getElementById('audio-element');
    if (!audioEl || !audioEl.src) return;
    
    if (audioEl.paused) {
        audioEl.play();
        player.isPlaying = true;
        document.getElementById('play-icon').className = 'bi bi-pause-fill';
    } else {
        audioEl.pause();
        player.isPlaying = false;
        document.getElementById('play-icon').className = 'bi bi-play-fill';
    }
}

function updateProgress() {
    const audioEl = document.getElementById('audio-element');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeEl = document.getElementById('current-time');
    const totalTimeEl = document.getElementById('total-time');
    
    if (audioEl.duration) {
        const progress = (audioEl.currentTime / audioEl.duration) * 100;
        progressBar.value = progress;
        currentTimeEl.textContent = formatTime(audioEl.currentTime);
        totalTimeEl.textContent = formatTime(audioEl.duration);
    }
}

function onTrackEnded() {
    document.getElementById('play-icon').className = 'bi bi-play-fill';
    player.isPlaying = false;
}

function closePlayer() {
    const audioEl = document.getElementById('audio-element');
    if (audioEl) {
        audioEl.pause();
        audioEl.src = '';
    }
    document.getElementById('music-player').classList.add('d-none');
}

function playerShuffle() {
    // Could implement shuffle queue here
    showToast('Shuffle enabled');
}

function playerPrev() {
    const audioEl = document.getElementById('audio-element');
    if (audioEl) audioEl.currentTime = 0;
}

function playerNext() {
    showToast('Next track');
}

function playerRepeat() {
    const audioEl = document.getElementById('audio-element');
    if (audioEl) audioEl.loop = !audioEl.loop;
    showToast(audioEl.loop ? 'Repeat on' : 'Repeat off');
}

// Volume control
document.addEventListener('DOMContentLoaded', function() {
    const volumeBar = document.getElementById('volume-bar');
    const progressBar = document.getElementById('progress-bar');
    
    if (volumeBar) {
        volumeBar.addEventListener('input', function() {
            const audioEl = document.getElementById('audio-element');
            if (audioEl) audioEl.volume = this.value / 100;
        });
    }
    
    if (progressBar) {
        progressBar.addEventListener('input', function() {
            const audioEl = document.getElementById('audio-element');
            if (audioEl && audioEl.duration) {
                audioEl.currentTime = (this.value / 100) * audioEl.duration;
            }
        });
    }
});

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 start-50 translate-middle-x mb-5 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

// ==================== CSRF Helper ====================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
