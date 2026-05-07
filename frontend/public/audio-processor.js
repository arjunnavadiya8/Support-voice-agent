class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 4096; // 4096 samples per chunk
        this._bytesWritten = 0;
        this._buffer = new Float32Array(this.bufferSize);
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0];
            for (let i = 0; i < channelData.length; i++) {
                this._buffer[this._bytesWritten++] = channelData[i];
                if (this._bytesWritten >= this.bufferSize) {
                    this.flush();
                }
            }
        }
        return true;
    }

    flush() {
        // We have 4096 Float32 samples.
        // Convert Float32 to Int16
        const int16Buffer = new Int16Array(this.bufferSize);
        for (let i = 0; i < this.bufferSize; i++) {
            let s = Math.max(-1, Math.min(1, this._buffer[i]));
            int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Send back to main thread
        this.port.postMessage(int16Buffer.buffer, [int16Buffer.buffer]);
        this._bytesWritten = 0;
        this._buffer = new Float32Array(this.bufferSize);
    }
}

registerProcessor("pcm-processor", PCMProcessor);
