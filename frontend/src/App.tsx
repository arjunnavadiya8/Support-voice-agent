    import { useVoiceAgent } from "./hooks/useVoiceAgent";
import { VoiceButton } from "./components/VoiceButton";
import { Transcript } from "./components/Transcript";

export default function App() {
    const { messages, status, startRecording, stopRecording, disconnect } = useVoiceAgent();

    return (
        <div
            style={{
                width: "100vw",
                minHeight: "100vh",
                background: "#050811", // Premium solid deep dark blue/black
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "2rem 1rem",
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                color: "#FFFFFF",
                overflowX: "hidden",
            }}
        >
            <div
                style={{
                    width: "100%",
                    maxWidth: 480,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    textAlign: "center",
                }}
            >
                {/* 1. Centered Audio Waveform Bars */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 28 }}>
                    <div
                        style={{
                            width: 4,
                            height: status === "speaking" ? 24 : status === "listening" ? 18 : 12,
                            background: "#3B82F6",
                            borderRadius: 2,
                            transition: "height 0.2s ease-in-out",
                        }}
                    />
                    <div
                        style={{
                            width: 4,
                            height: status === "speaking" ? 40 : status === "listening" ? 30 : 24,
                            background: "#3B82F6",
                            borderRadius: 2,
                            transition: "height 0.2s ease-in-out",
                        }}
                    />
                    <div
                        style={{
                            width: 4,
                            height: status === "speaking" ? 56 : status === "listening" ? 48 : 40,
                            background: "#4F46E5",
                            borderRadius: 2,
                            transition: "height 0.2s ease-in-out",
                        }}
                    />
                    <div
                        style={{
                            width: 4,
                            height: status === "speaking" ? 40 : status === "listening" ? 30 : 24,
                            background: "#3B82F6",
                            borderRadius: 2,
                            transition: "height 0.2s ease-in-out",
                        }}
                    />
                    <div
                        style={{
                            width: 4,
                            height: status === "speaking" ? 24 : status === "listening" ? 18 : 12,
                            background: "#3B82F6",
                            borderRadius: 2,
                            transition: "height 0.2s ease-in-out",
                        }}
                    />
                </div>

                {/* 2. Text Titles */}
                <h2 style={{ fontWeight: 600, fontSize: "24px", color: "#FFFFFF", marginBottom: 8, letterSpacing: "-0.01em" }}>
                    Talk to your AI assistant
                </h2>
                <p style={{ fontSize: "14px", color: "#8E9AA8", marginBottom: 48, fontWeight: 400, maxWidth: "80%" }}>
                    Click the button below to start a conversation
                </p>

                {/* 3. Centered Large Mic Button */}
                <div style={{ marginBottom: 32 }}>
                    <VoiceButton
                        status={status}
                        onStart={startRecording}
                        onStop={stopRecording}
                        onDisconnect={disconnect}
                    />
                </div>

                {/* 4. Chat Transcript Container */}
                <Transcript messages={messages} />
            </div>
        </div>
    );
}