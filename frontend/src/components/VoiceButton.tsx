import { useEffect, useRef } from "react";

type Props = {
    status: "idle" | "listening" | "processing" | "speaking";
    onStart: () => void;
    onStop: () => void;
    onDisconnect: () => void;
};

export function VoiceButton({ status, onStart, onStop, onDisconnect }: Props) {
    const audioRef = useRef<HTMLAudioElement>(null);

    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.src = "";
            }
        };
    }, []);

    const handleClick = () => {
        if (status === "idle") {
            onStart();
        } else if (status === "listening") {
            onStop();
        } else {
            // If processing or speaking, clicking acts as "Hang Up" / Interrupt
            onDisconnect();
        }
    };

    const getButtonBg = () => {
        if (status === "listening") return "#EF4444"; // Solid Red (Listening)
        if (status === "processing") return "#4B5563"; // Muted gray-blue (Processing)
        if (status === "speaking") return "#EF4444"; // Solid Red (Can stop speaking anytime)
        return "#2563EB"; // Solid Premium Blue (Idle)
    };

    const getStatusText = () => {
        if (status === "idle") return "Tap to talk";
        if (status === "listening") return "Listening... Click to stop";
        if (status === "processing") return "Processing... Click to cancel";
        if (status === "speaking") return "Speaking... Click to stop";
        return "Tap to talk";
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            {/* Outer Elegant Ring */}
            <div
                style={{
                    width: 110,
                    height: 110,
                    borderRadius: "50%",
                    border: status === "idle" ? "1.5px solid #1E293B" : "1.5px solid #EF4444",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    transition: "all 0.3s ease",
                    boxShadow: status !== "idle" ? "0 0 15px rgba(239, 68, 68, 0.2)" : "none",
                }}
            >
                {/* Inner Microphone Button */}
                <button
                    onClick={handleClick}
                    style={{
                        width: 84,
                        height: 84,
                        borderRadius: "50%",
                        border: "none",
                        background: getButtonBg(),
                        color: "#fff",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        cursor: "pointer",
                        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                        outline: "none",
                    }}
                >
                    {status === "processing" ? (
                        /* Stop square icon for canceling processing */
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                            style={{ width: 28, height: 28 }}
                        >
                            <rect x="4" y="4" width="16" height="16" rx="2" />
                        </svg>
                    ) : status === "listening" || status === "speaking" ? (
                        /* Stop square icon for ending call */
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                            style={{ width: 28, height: 28 }}
                        >
                            <rect x="4" y="4" width="16" height="16" rx="2" />
                        </svg>
                    ) : (
                        /* Mic icon for starting call */
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                            style={{ width: 30, height: 30 }}
                        >
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" />
                        </svg>
                    )}
                </button>
            </div>

            {/* Status Text Below */}
            <span style={{ fontSize: 13, color: "#8E9AA8", fontWeight: 500, letterSpacing: "0.02em" }}>
                {getStatusText()}
            </span>
            <audio ref={audioRef} style={{ display: "none" }} />
        </div>
    );
}
