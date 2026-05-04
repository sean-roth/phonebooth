import { Device, Call } from '@twilio/voice-sdk';

export class PhoneboothDevice {
    constructor() {
        this.device = null;
        this.activeCall = null;
        this.onStatusChange = null;
    }

    async initialize() {
        const response = await fetch('/api/twilio/token');
        const data = await response.json();

        if (data.error) {
            this.notify('not-configured', data.error);
            return;
        }

        this.device = new Device(data.token, {
            logLevel: 1,
            codecPreferences: [Call.Codec.Opus, Call.Codec.PCMU],
        });

        this.device.on('registered', () => this.notify('idle'));
        this.device.on('error', (error) => {
            console.error('Twilio Device error:', error);
            this.notify('error', error);
        });

        // Request mic permission early so prompt appears on page load, not mid-dial
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (err) {
            console.error('Microphone access denied:', err);
            this.notify('mic-denied');
            return;
        }

        await this.device.register();
    }

    async call(phoneNumber, callId) {
        if (!this.device) throw new Error('Device not initialized');

        this.notify('connecting');
        this.activeCall = await this.device.connect({
            params: {
                To: phoneNumber,
                call_id: String(callId),
            },
        });

        this.activeCall.on('accept', () => this.notify('on-call'));
        this.activeCall.on('disconnect', () => {
            this.notify('call-ended');
            this.activeCall = null;
        });
        this.activeCall.on('cancel', () => {
            this.notify('idle');
            this.activeCall = null;
        });
        this.activeCall.on('reject', () => {
            this.notify('idle');
            this.activeCall = null;
        });

        return this.activeCall;
    }

    hangup() {
        if (this.activeCall) {
            this.activeCall.disconnect();
        }
    }

    notify(status, payload = null) {
        if (this.onStatusChange) {
            this.onStatusChange(status, payload);
        }
    }
}
