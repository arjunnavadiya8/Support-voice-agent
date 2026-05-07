import { useCallback, useEffect, useRef, useState } from "react";

export type Message = {
    role: "user" | "agent";
    text: string;
    language?: string;
};

type Status = "idle" | "listening" | "processing" | "speaking";

export function useVoiceAgent() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [status, setStatus] = useState<Status>("idle");

    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const workletNodeRef = useRef<AudioWorkletNode | null>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Playback state
    const playContextRef = useRef<AudioContext | null>(null);
    const nextPlayTimeRef = useRef<number>(0);

    const connect = useCallback(async () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return wsRef.current;
        }

        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const ws = new WebSocket(`${protocol}://${window.location.host}/ws/voice`);
        ws.binaryType = "arraybuffer"; // Support binary audio data
        wsRef.current = ws;

        await new Promise<void>((resolve, reject) => {
            ws.addEventListener("open", () => resolve(), { once: true });
            ws.addEventListener("error", () => reject(new Error("WebSocket connection failed")), { once: true });
        });

        // Initialize AudioContext for playback if not done
        if (!playContextRef.current) {
            playContextRef.current = new AudioContext({ sampleRate: 22050 });
        }

        ws.onmessage = async (event) => {
            if (event.data instanceof ArrayBuffer) {
                // Incoming TTS PCM stream
                if (playContextRef.current) {
                    const int16Array = new Int16Array(event.data);
                    const float32Array = new Float32Array(int16Array.length);
                    for (let i = 0; i < int16Array.length; i++) {
                        float32Array[i] = int16Array[i] / 32768.0;
                    }

                    const audioBuffer = playContextRef.current.createBuffer(1, float32Array.length, 22050);
                    audioBuffer.getChannelData(0).set(float32Array);

                    const source = playContextRef.current.createBufferSource();
                    source.buffer = audioBuffer;
                    source.connect(playContextRef.current.destination);

                    if (nextPlayTimeRef.current < playContextRef.current.currentTime) {
                        nextPlayTimeRef.current = playContextRef.current.currentTime;
                    }

                    source.start(nextPlayTimeRef.current);
                    nextPlayTimeRef.current += audioBuffer.duration;
                }
                return;
            }

            const message = JSON.parse(event.data);
            
            if (message.type === "transcript_update") {
                // Ignore interim transcripts for UI, but could be used to show live typing
            } else if (message.type === "transcript") {
                setMessages((prev) => [...prev, { role: "user", text: message.user, language: message.language }]);
            } else if (message.type === "assistant_chunk") {
                // Realtime text stream could be shown here
            } else if (message.type === "assistant_end") {
                setMessages((prev) => [...prev, { role: "agent", text: message.text, language: message.language }]);
            } else if (message.type === "state") {
                if (message.state === "thinking") setStatus("processing");
                else if (message.state === "speaking") setStatus("speaking");
                else if (message.state === "listening") setStatus("listening");
                else if (message.state === "interrupted") setStatus("listening");
            } else if (message.type === "clear_queue") {
                // Stop all ongoing playback instantly
                if (playContextRef.current) {
                    playContextRef.current.close();
                    playContextRef.current = new AudioContext({ sampleRate: 22050 });
                    nextPlayTimeRef.current = 0;
                }
            } else if (message.type === "error") {
                console.error(message.message);
                setStatus("idle");
            }
        };

        ws.onclose = () => {
            wsRef.current = null;
            setStatus("idle");
        };

        return ws;
    }, []);

    const disconnect = useCallback(() => {
        if (workletNodeRef.current) {
            workletNodeRef.current.disconnect();
            workletNodeRef.current = null;
        }

        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }

        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        if (playContextRef.current) {
            playContextRef.current.close();
            playContextRef.current = null;
        }

        setStatus("idle");
    }, []);

    const startRecording = useCallback(async () => {
        if (status !== "idle") return;

        const ws = await connect();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
        streamRef.current = stream;

        // Force 16kHz context for deepgram
        const audioContext = new AudioContext({ sampleRate: 16000 });
        audioContextRef.current = audioContext;

        await audioContext.audioWorklet.addModule("/audio-processor.js");

        const source = audioContext.createMediaStreamSource(stream);
        const processor = new AudioWorkletNode(audioContext, "pcm-processor");
        workletNodeRef.current = processor;

        processor.port.onmessage = (event) => {
            if (ws.readyState === WebSocket.OPEN) {
                // Send raw PCM ArrayBuffer
                ws.send(event.data);
            }
        };

        source.connect(processor);
        // Do not connect processor to destination to avoid loopback
        
        setStatus("listening");
    }, [connect, status]);

    const stopRecording = useCallback(() => {
        disconnect();
    }, [disconnect]);

    useEffect(() => () => disconnect(), [disconnect]);

    return {
        messages,
        status,
        startRecording,
        stopRecording,
        disconnect,
        startCall: startRecording,
        stopCall: stopRecording,
    };
}
