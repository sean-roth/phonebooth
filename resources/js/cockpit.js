import { PhoneboothDevice } from './twilio-device';

const device = new PhoneboothDevice();
let currentCallId = null;
let timerInterval = null;
let timerStart = null;

const callBtn = document.getElementById('call-btn');
const hangupBtn = document.getElementById('hangup-btn');
const statusEl = document.getElementById('call-status');
const timerEl = document.getElementById('call-timer');
const postCallForm = document.getElementById('post-call-form');
const actionInput = document.getElementById('action-input');
const phoneNumber = callBtn.dataset.phone;
const leadId = callBtn.dataset.leadId;

device.onStatusChange = (status, payload) => {
    statusEl.textContent = statusLabel(status);
    statusEl.className = 'text-sm font-medium ' + statusColor(status);

    if (status === 'on-call') {
        timerStart = Date.now();
        timerInterval = setInterval(updateTimer, 1000);
        callBtn.classList.add('hidden');
        hangupBtn.classList.remove('hidden');
    } else if (status === 'call-ended') {
        clearInterval(timerInterval);
        callBtn.classList.remove('hidden');
        hangupBtn.classList.add('hidden');
        if (currentCallId) {
            enablePostCallForm();
        }
    } else if (status === 'idle') {
        callBtn.classList.remove('hidden');
        hangupBtn.classList.add('hidden');
        callBtn.disabled = false;
    } else if (status === 'connecting') {
        callBtn.disabled = true;
    } else if (status === 'error') {
        alert('Call failed: ' + (payload?.message || 'unknown error'));
        callBtn.disabled = false;
        callBtn.classList.remove('hidden');
        hangupBtn.classList.add('hidden');
    } else if (status === 'not-configured') {
        callBtn.disabled = true;
        callBtn.textContent = 'Phone Not Configured';
    } else if (status === 'mic-denied') {
        callBtn.disabled = true;
        callBtn.textContent = 'Microphone Access Required';
    }
};

callBtn.addEventListener('click', async () => {
    // Disable immediately to prevent double-click creating duplicate call records
    callBtn.disabled = true;

    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    const response = await fetch('/calls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': csrfToken,
        },
        body: JSON.stringify({ lead_id: leadId }),
    });

    if (!response.ok) {
        alert('Failed to create call record. Check console.');
        console.error('Call store failed:', await response.text());
        callBtn.disabled = false;
        return;
    }

    const data = await response.json();
    currentCallId = data.call_id;

    await device.call(phoneNumber, currentCallId);
});

hangupBtn.addEventListener('click', () => {
    device.hangup();
});

// Save and Next / Save and Stay buttons
document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', () => {
        actionInput.value = btn.dataset.action;
    });
});

function updateTimer() {
    const elapsed = Math.floor((Date.now() - timerStart) / 1000);
    const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const secs = (elapsed % 60).toString().padStart(2, '0');
    timerEl.textContent = `${mins}:${secs}`;
}

function enablePostCallForm() {
    postCallForm.action = '/calls/' + currentCallId;
    postCallForm.querySelectorAll('input, select, textarea, button').forEach(el => {
        el.disabled = false;
    });
    postCallForm.classList.remove('opacity-50');
}

function statusLabel(status) {
    const labels = {
        'idle': 'Ready',
        'connecting': 'Connecting...',
        'on-call': 'On Call',
        'call-ended': 'Call Ended',
        'error': 'Error',
        'not-configured': 'Phone Not Configured',
        'mic-denied': 'Mic Access Denied',
    };
    return labels[status] || status;
}

function statusColor(status) {
    const colors = {
        'idle': 'text-green-600',
        'connecting': 'text-yellow-600',
        'on-call': 'text-blue-600',
        'call-ended': 'text-gray-600',
        'error': 'text-red-600',
        'not-configured': 'text-orange-600',
        'mic-denied': 'text-red-600',
    };
    return colors[status] || 'text-gray-600';
}

document.addEventListener('DOMContentLoaded', () => {
    device.initialize().catch(err => {
        console.error('Failed to initialize Twilio:', err);
        statusEl.textContent = 'Phone initialization failed';
        statusEl.className = 'text-sm font-medium text-red-600';
    });
});
