import React, { useEffect, useRef, useState } from "react";
import { useVoiceAgent, Status } from "./hooks/useVoiceAgent";

// Extracted Styles to exactly match original reference CSS
const styles = {
    bg: "#0f0f0f",
    surface: "#1a1a1a",
    border: "#2e2e2e",
    text: "#f0f0f0",
    muted: "#777",
    blue: "#3b82f6",
    red: "#ef4444",
    green: "#22c55e",
    amber: "#f59e0b",
    userBg: "#1e3a5f",
    agentBg: "#1a2e1a",
};

export default function App() {
    const {
        messages,
        interimText,
        status,
        vadEnergy,
        callActive,
        analyserRef,
        startCall,
        stopCall,
        setVolume,
        isMuted,
        toggleMute,
        currentLang,
        setCurrentLang,
    } = useVoiceAgent();

    const chatRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const rafRef = useRef<number | null>(null);
    const [inputVol, setInputVol] = useState(1);

    // Automatic Autoscroll for messages
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages, interimText]);

    // Live Waveform Canvas Drawer Logic mirroring original test UI
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const data = new Uint8Array(analyserRef.current ? analyserRef.current.fftSize : 256);

        function draw() {
            if (!canvas || !ctx) return;
            rafRef.current = requestAnimationFrame(draw);

            if (analyserRef.current) {
                analyserRef.current.getByteTimeDomainData(data);
            } else {
                data.fill(128); // static line if not connected
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.beginPath();
            const sl = canvas.width / data.length;
            let x = 0;

            for (let i = 0; i < data.length; i++) {
                const y = ((data[i] / 128) - 1) * (canvas.height / 2) + canvas.height / 2;
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                x += sl;
            }

            // Color based on mode: green for mic listening, blue for agent speaking
            ctx.strokeStyle = status === "speaking" ? styles.blue : status === "processing" ? styles.amber : styles.green;
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }

        draw();
        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [analyserRef, status]);

    const handleToggle = () => {
        if (!callActive) {
            startCall(currentLang);
        } else {
            stopCall();
        }
    };

    const onVolChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const v = parseFloat(e.target.value);
        setInputVol(v);
        setVolume(v);
    };

    // Helper to render the status text
    const getStatusText = () => {
        if (!callActive) return "Ready — press 📞 to start";
        if (status === "listening") return "Listening…";
        if (status === "processing") return "Thinking…";
        if (status === "speaking") return "Speaking…";
        return "Connecting…";
    };

    return (
        <div style={{
            height: "100vh",
            width: "100vw",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: styles.bg,
            color: styles.text,
            fontFamily: "system-ui, -apple-system, sans-serif",
            margin: 0,
            overflow: "hidden",
        }}>
            <style>{`
                @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
                @keyframes rise { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
                @keyframes callpulse {
                    0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
                    70% { box-shadow: 0 0 0 18px rgba(59, 130, 246, 0); }
                }
                @keyframes callpulse-red {
                    0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
                    70% { box-shadow: 0 0 0 18px rgba(239, 68, 68, 0); }
                }
                .scroll-hide::-webkit-scrollbar { width: 4px; }
                .scroll-hide::-webkit-scrollbar-thumb { background: ${styles.border}; border-radius: 2px; }
            `}</style>

            {/* MAIN CARD CONTAINER */}
            <div style={{
                width: "100%",
                maxWidth: "440px",
                background: styles.surface,
                border: `1px solid ${styles.border}`,
                borderRadius: "24px",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                boxShadow: "0 8px 48px rgba(0,0,0,0.7)",
            }}>

                {/* HEADER */}
                <div style={{ padding: "1rem 1.4rem", borderBottom: `1px solid ${styles.border}`, display: "flex", alignItems: "center", gap: "12px" }}>
                    <div style={{
                        width: "42px", height: "42px", borderRadius: "50%",
                        background: styles.blue, display: "flex", alignItems: "center",
                        justifyContent: "center", fontSize: "1.1rem", fontWeight: 600, flexShrink: 0,
                    }}>
                        S
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "0.95rem", fontWeight: 500 }}>Suvit Support</div>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "3px" }}>
                            <div style={{
                                width: "7px", height: "7px", borderRadius: "50%",
                                background: !callActive ? styles.border 
                                           : status === "listening" ? styles.green 
                                           : status === "speaking" ? styles.blue 
                                           : styles.amber,
                                animation: callActive ? "blink 1s ease-in-out infinite" : "none"
                            }} />
                            <span style={{ fontSize: "0.74rem", color: styles.muted }}>{getStatusText()}</span>
                        </div>
                    </div>
                    <div style={{ fontSize: "0.7rem", color: styles.muted, opacity: 0.5 }}>⚙️</div>
                </div>

                {/* LANGUAGE SELECTOR PILLS */}
                <div style={{ display: "flex", gap: "6px", padding: "0.65rem 1.4rem", borderBottom: `1px solid ${styles.border}` }}>
                    {["en", "hi", "gu"].map(l => (
                        <button
                            key={l}
                            onClick={() => { if(!callActive) setCurrentLang(l); }}
                            disabled={callActive}
                            style={{
                                padding: "4px 16px", borderRadius: "20px",
                                border: `1px solid ${currentLang === l ? styles.blue : styles.border}`,
                                background: currentLang === l ? styles.blue : "transparent",
                                color: currentLang === l ? "#fff" : styles.muted,
                                fontSize: "0.78rem", cursor: callActive ? "default" : "pointer",
                                transition: "all 0.15s", opacity: callActive && currentLang !== l ? 0.4 : 1
                            }}
                        >
                            {l === "en" ? "English" : l === "hi" ? "Hindi" : "Gujarati"}
                        </button>
                    ))}
                </div>

                {/* CHAT HISTORY CONVERSATION */}
                <div ref={chatRef} className="scroll-hide" style={{
                    flex: 1,
                    minHeight: "280px",
                    maxHeight: "360px",
                    overflowY: "auto",
                    padding: "1rem 1.2rem",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.65rem",
                }}>
                    {messages.length === 0 && !callActive ? (
                        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "0.5rem", color: styles.muted, fontSize: "0.85rem", textAlign: "center" }}>
                            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📞</div>
                            <div>Press the call button to connect</div>
                            <div style={{ fontSize: "0.72rem", opacity: 0.6, marginTop: "0.2rem" }}>
                                English · Hindi · Gujarati
                            </div>
                        </div>
                    ) : (
                        messages.map((m, i) => (
                            <div
                                key={i}
                                style={{
                                    maxWidth: "82%",
                                    padding: m.role === "system" ? "2px 0" : "0.6rem 0.9rem",
                                    borderRadius: "16px",
                                    fontSize: m.role === "system" ? "0.72rem" : "0.86rem",
                                    lineHeight: "1.6",
                                    animation: "rise 0.2s ease",
                                    alignSelf: m.role === "user" ? "flex-end" : m.role === "agent" ? "flex-start" : "center",
                                    background: m.role === "user" ? styles.userBg : m.role === "agent" ? styles.agentBg : "none",
                                    borderBottomRightRadius: m.role === "user" ? "4px" : "16px",
                                    borderBottomLeftRadius: m.role === "agent" ? "4px" : "16px",
                                    color: m.role === "system" ? styles.muted : styles.text,
                                }}
                            >
                                {m.text}
                                {m.language && m.role !== "system" && (
                                    <span style={{
                                        fontSize: "0.65rem", fontWeight: 600,
                                        padding: "1px 6px", borderRadius: "8px",
                                        marginLeft: "6px",
                                        background: m.language === "en" ? "#1e3a5f" : m.language === "hi" ? "#1e2d1e" : "#2d2010",
                                        color: m.language === "en" ? "#7cb9f8" : m.language === "hi" ? "#86efac" : "#fcd34d"
                                    }}>
                                        {m.language.toUpperCase()}
                                    </span>
                                )}
                            </div>
                        ))
                    )}

                    {/* Interim Realtime Transcript Display */}
                    {interimText && (
                        <div
                            style={{
                                maxWidth: "82%",
                                padding: "0.6rem 0.9rem",
                                borderRadius: "16px",
                                fontSize: "0.86rem",
                                lineHeight: "1.6",
                                alignSelf: "flex-end",
                                background: styles.userBg,
                                borderBottomRightRadius: "4px",
                                color: styles.text,
                                opacity: 0.6,
                                fontStyle: "italic",
                            }}
                        >
                            {interimText}…
                        </div>
                    )}
                </div>

                {/* VAD ENERGY METER (DYNAMIC WIDTH BAR) */}
                <div style={{ height: "3px", background: styles.border, borderRadius: "2px", margin: "0 1.2rem" }}>
                    <div style={{
                        height: "100%",
                        background: styles.green,
                        borderRadius: "2px",
                        transition: "width 0.05s linear",
                        width: `${Math.min(100, vadEnergy)}%`
                    }} />
                </div>

                {/* OSCILLOSCOPE CANVAS CONTAINER */}
                <div style={{ height: "52px", padding: "0 1.2rem", borderTop: `1px solid ${styles.border}`, display: "flex", alignItems: "center" }}>
                    <canvas ref={canvasRef} width={400} height={38} style={{ width: "100%", height: "38px" }} />
                </div>

                {/* FOOTER CONTROLS */}
                <div style={{
                    padding: "0.85rem 1.4rem 1.1rem",
                    borderTop: `1px solid ${styles.border}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                }}>
                    {/* VOLUME SLIDER */}
                    <div style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "0.8rem", color: styles.muted }}>
                        🔈
                        <input
                            type="range"
                            min="0"
                            max="2"
                            step="0.05"
                            value={inputVol}
                            onChange={onVolChange}
                            style={{ width: "70px", accentColor: styles.blue, cursor: "pointer" }}
                        />
                        🔊
                    </div>

                    {/* BIG CENTER CALL BUTTON */}
                    <button
                        onClick={handleToggle}
                        style={{
                            width: "64px",
                            height: "64px",
                            borderRadius: "50%",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "1.5rem",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: callActive ? styles.red : styles.blue,
                            color: "#fff",
                            transition: "all 0.2s",
                            animation: callActive ? "callpulse-red 1.5s ease-in-out infinite" : "none",
                            transform: "scale(1)",
                        }}
                        onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.94)")}
                        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
                    >
                        {callActive ? "📵" : "📞"}
                    </button>

                    {/* RIGHT MUTE TOGGLE */}
                    <div style={{ width: "90px", display: "flex", justifyContent: "flex-end" }}>
                        <button
                            onClick={toggleMute}
                            disabled={!callActive}
                            style={{
                                width: "40px",
                                height: "40px",
                                borderRadius: "50%",
                                border: `1px solid ${!callActive ? "transparent" : isMuted ? styles.red : styles.border}`,
                                background: !callActive ? "transparent" : isMuted ? styles.red : "rgba(255,255,255,0.05)",
                                color: !callActive ? "#444" : "#fff",
                                fontSize: "1rem",
                                cursor: callActive ? "pointer" : "default",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                transition: "all 0.2s",
                                opacity: !callActive ? 0.3 : 1
                            }}
                            title={!callActive ? "Mute unavailable outside call" : isMuted ? "Unmute" : "Mute Microphone"}
                        >
                            {isMuted ? "🔇" : "🎤"}
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}