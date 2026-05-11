class MicProcessor extends AudioWorkletProcessor {
  constructor(opts) {
    super();
    this._tgtSR  = opts.processorOptions?.targetSR || 16000;
    this._ratio  = sampleRate / this._tgtSR;   
    this._pcmBuf = [];
    
    this._energy  = 0; // Still keep energy visualization for the UI bar
    this._agentOn = false;

    this.port.onmessage = ({data}) => {
      if (data.type === 'agent_speaking') this._agentOn = data.v;
    };
  }

  process(inputs) {
    const ch = inputs[0]?.[0];
    if (!ch || ch.length === 0) return true;

    // 1. Compute energy strictly for UI visualization bar, NOT for gating
    let sum = 0;
    for (let i = 0; i < ch.length; i++) sum += ch[i] * ch[i];
    const rms = Math.sqrt(sum / ch.length);
    this._energy = this._energy * 0.85 + rms * 0.15;
    this.port.postMessage({ type: 'energy', v: this._energy });

    // 2. Continuous Streaming Pipeline
    // We pipe EVERYTHING to Deepgram Neural Cloud continuously to allow
    // true server-side barge-in. The local OS echo cancellation handle filters loopback.

    // Downsample Float32@48kHz → Int16@16kHz directly
    for (let i = 0; i < ch.length; i += this._ratio) {
      const idx = Math.round(i);
      if(idx < ch.length) this._pcmBuf.push(ch[idx]);
    }

    // Emit when buffer fills 4096 samples
    while (this._pcmBuf.length >= 4096) {
      const slice = this._pcmBuf.splice(0, 4096);
      const i16   = new Int16Array(4096);
      for (let i = 0; i < 4096; i++)
        i16[i] = Math.max(-32768, Math.min(32767, slice[i] * 32767));
      this.port.postMessage({ type: 'pcm', buf: i16.buffer }, [i16.buffer]);
    }

    return true;
  }
}

registerProcessor('pcm-processor', MicProcessor);
