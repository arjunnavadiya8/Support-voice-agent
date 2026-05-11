import { useCallback, useEffect, useRef, useState } from "react";

export type Message = {
    role: "user" | "agent" | "system";
    text: string;
    language?: string;
};

export type Status = "idle" | "listening" | "processing" | "speaking";

export function useVoiceAgent() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [status, setStatus] = useState<Status>("idle");
    const [vadEnergy, setVadEnergy] = useState<number>(0);
    const [currentLang, setCurrentLang] = useState<string>("en");
    const [callActive, setCallActive] = useState<boolean>(false);
    const [isMuted, setIsMuted] = useState<boolean>(false);
    const [interimText, setInterimText] = useState<string>("");

    const wsRef = useRef<WebSocket | null>(null);
    const micCtxRef = useRef<AudioContext | null>(null);
    const workletNodeRef = useRef<AudioWorkletNode | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    
    const agentSpeakingRef = useRef<boolean>(false);
    const interruptSentRef = useRef<boolean>(false);

    // Playback context (typically 22050 for ElevenLabs/Sarvam output)
    const playContextRef = useRef<AudioContext | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);
    const nextPlayTimeRef = useRef<number>(0);

    const setAgentSpeaking = useCallback((isSpeaking: boolean) => {
        agentSpeakingRef.current = isSpeaking;
        if (isSpeaking) {
            interruptSentRef.current = false; // Reset interrupt lock on new burst
            setStatus("speaking");
        }
        if (workletNodeRef.current) {
            workletNodeRef.current.port.postMessage({ type: 'agent_speaking', v: isSpeaking });
        }
    }, []);

    const stopPlayback = useCallback(() => {
        if (playContextRef.current && playContextRef.current.state !== "closed") {
            playContextRef.current.close().catch(() => {});
        }
        playContextRef.current = null;
        gainNodeRef.current = null;
        nextPlayTimeRef.current = 0;
        setAgentSpeaking(false);
    }, [setAgentSpeaking]);

    const ensurePlayCtx = useCallback(() => {
        if (playContextRef.current && playContextRef.current.state !== "closed") return;
        playContextRef.current = new AudioContext({ sampleRate: 22050 });
        gainNodeRef.current = playContextRef.current.createGain();
        gainNodeRef.current.gain.value = 1.0; // Default volume
        gainNodeRef.current.connect(playContextRef.current.destination);
        nextPlayTimeRef.current = 0;
    }, []);

    const disconnect = useCallback((shouldResetMessages: boolean = false) => {
        setCallActive(false);
        
        if (workletNodeRef.current) {
            workletNodeRef.current.disconnect();
            workletNodeRef.current = null;
        }
        if (analyserRef.current) {
            analyserRef.current.disconnect();
            analyserRef.current = null;
        }
        if (micCtxRef.current) {
            micCtxRef.current.close().catch(() => {});
            micCtxRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
        }
        
        stopPlayback();

        if (wsRef.current) {
            if (wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: "call_end" }));
            }
            wsRef.current.close();
            wsRef.current = null;
        }

        setStatus("idle");
        setVadEnergy(0);
        setIsMuted(false); // Reset mute state for next call
        if(shouldResetMessages) setMessages([]);
    }, [stopPlayback]);

    const connect = useCallback(async (languageSelection: string) => {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const ws = new WebSocket(`${protocol}://${window.location.host}/ws/call`);
        ws.binaryType = "arraybuffer"; 
        wsRef.current = ws;

        await new Promise<void>((resolve, reject) => {
            ws.addEventListener("open", () => {
                ws.send(JSON.stringify({ type: "call_start", language: languageSelection }));
                resolve();
            }, { once: true });
            ws.addEventListener("error", () => reject(new Error("WS connection failed")), { once: true });
        });

        ws.onmessage = (event) => {
            // 1. Raw audio binary from Agent
            if (event.data instanceof ArrayBuffer) {
                if (!agentSpeakingRef.current) return; // discard late arrivals
                ensurePlayCtx();
                if (!playContextRef.current || !gainNodeRef.current) return;

                const i16Array = new Int16Array(event.data);
                const f32Array = new Float32Array(i16Array.length);
                for (let i = 0; i < i16Array.length; i++) f32Array[i] = i16Array[i] / 32768.0;

                const audioBuf = playContextRef.current.createBuffer(1, f32Array.length, 22050);
                audioBuf.getChannelData(0).set(f32Array);

                const src = playContextRef.current.createBufferSource();
                src.buffer = audioBuf;
                src.connect(gainNodeRef.current);

                const now = playContextRef.current.currentTime;
                const when = Math.max(now + 0.01, nextPlayTimeRef.current);
                src.start(when);
                nextPlayTimeRef.current = when + audioBuf.duration;
                return;
            }

            // 2. JSON Protocol
            const message = JSON.parse(event.data);
            switch (message.type) {
                case "call_accepted":
                    setStatus("listening");
                    break;
                case "status":
                    if (message.message.includes("Transcrib") || message.message.includes("Think")) {
                        setStatus("processing");
                    } else {
                        setStatus("listening");
                    }
                    break;
                case "transcript":
                    setMessages(prev => [...prev, { role: "user", text: message.user, language: message.language }]);
                    setInterimText(""); // clear ephemeral
                    break;
                case "transcript_update":
                    // Dynamic rolling partial text from Deepgram live stream
                    setInterimText(message.text);
                    break;
                case "assistant_end":
                    setMessages(prev => [...prev, { role: "agent", text: message.text, language: message.language }]);
                    break;
                case "tts_start":
                    setAgentSpeaking(true);
                    ensurePlayCtx();
                    break;
                case "tts_end":
                    setAgentSpeaking(false);
                    setStatus("listening");
                    break;
                case "clear_queue":
                    stopPlayback();
                    setStatus("listening");
                    break;
                case "call_ended":
                    setMessages(prev => [...prev, { role: "agent", text: message.message || "Goodbye!", language: "en" }]);
                    // Don't immediately disconnect so user reads goodbye, or disconnect(false)
                    break;
                case "error":
                    setMessages(prev => [...prev, { role: "system", text: "⚠ " + message.message }]);
                    break;
            }
        };

        ws.onclose = () => {
            wsRef.current = null;
            // Auto cleanup if remote drops
            if (callActive) disconnect(false);
        };

        return ws;
    }, [callActive, disconnect, ensurePlayCtx, setAgentSpeaking, stopPlayback]);

    const startCall = useCallback(async (lang: string) => {
        setMessages([]); // clear prior
        setCallActive(true);
        setCurrentLang(lang);
        
        try {
            // 1. Web Socket Init
            const ws = await connect(lang);

            // 2. Mic Initalization
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, sampleRate: 48000 } 
            });
            streamRef.current = stream;

            const micCtx = new AudioContext({ sampleRate: 48000 });
            micCtxRef.current = micCtx;

            // Add timestamp query param to force browser cache clear for new logic
            await micCtx.audioWorklet.addModule("/audio-processor.js?v3=" + Date.now());
            const srcNode = micCtx.createMediaStreamSource(stream);

            const analyser = micCtx.createAnalyser();
            analyser.fftSize = 256;
            srcNode.connect(analyser);
            analyserRef.current = analyser;

            const processor = new AudioWorkletNode(micCtx, "pcm-processor", {
                processorOptions: { targetSR: 16000 }
            });
            workletNodeRef.current = processor;

            processor.port.onmessage = ({ data }) => {
                if (data.type === "energy") {
                    setVadEnergy(Math.min(100, data.v * 1200));
                } else if (data.type === "pcm") {
                    // Pure throughput: Pipe raw audio bytes to server 24/7
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(data.buf); 
                    }
                }
            };

            srcNode.connect(processor);
            setStatus("listening");

        } catch (err: any) {
            setMessages(prev => [...prev, { role: "system", text: "⚠ Microphone access denied: " + err.message }]);
            setCallActive(false);
            disconnect(false);
        }
    }, [connect, disconnect, stopPlayback]);

    const setVolume = useCallback((val: number) => {
        if (gainNodeRef.current) {
            gainNodeRef.current.gain.value = val;
        }
    }, []);

    const toggleMute = useCallback(() => {
        if (!streamRef.current) return;
        const newState = !isMuted;
        setIsMuted(newState);
        
        // Physically toggle the audio tracks at the browser layer
        streamRef.current.getAudioTracks().forEach(track => {
            track.enabled = !newState; 
        });
    }, [isMuted]);

    // Cleanup entirely on unmount
    useEffect(() => {
        return () => {
            disconnect(false);
        };
    }, [disconnect]);

    return {
        messages,
        interimText,
        status,
        vadEnergy,
        callActive,
        analyserRef, // Exposing the ref so canvas draw can read it directly
        startCall,
        stopCall: () => disconnect(false),
        setVolume,
        isMuted,
        toggleMute,
        currentLang,
        setCurrentLang,
    };
}
