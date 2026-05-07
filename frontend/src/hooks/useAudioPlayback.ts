import { useCallback, useEffect, useRef } from "react";

export function useAudioPlayback() {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const mediaSourceRef = useRef<MediaSource | null>(null);
    const sourceBufferRef = useRef<SourceBuffer | null>(null);
    const queueRef = useRef<ArrayBuffer[]>([]);
    const objectUrlRef = useRef<string | null>(null);

    const clear = useCallback(() => {
        queueRef.current = [];
        sourceBufferRef.current = null;

        if (!audioRef.current) {
            audioRef.current = new Audio();
        }

        audioRef.current.pause();
        audioRef.current.src = "";

        if (objectUrlRef.current) {
            URL.revokeObjectURL(objectUrlRef.current);
            objectUrlRef.current = null;
        }

        mediaSourceRef.current = null;
    }, []);

    const flushQueue = useCallback(() => {
        const sourceBuffer = sourceBufferRef.current;
        if (!sourceBuffer || sourceBuffer.updating || queueRef.current.length === 0) {
            return;
        }
        sourceBuffer.appendBuffer(queueRef.current.shift()!);
    }, []);

    const start = useCallback(() => {
        clear();

        if (!audioRef.current) {
            audioRef.current = new Audio();
        }

        const mediaSource = new MediaSource();
        mediaSourceRef.current = mediaSource;
        objectUrlRef.current = URL.createObjectURL(mediaSource);
        audioRef.current.src = objectUrlRef.current;
        audioRef.current.play().catch(() => undefined);

        mediaSource.addEventListener("sourceopen", () => {
            if (mediaSource.readyState !== "open") {
                return;
            }

            const sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
            sourceBufferRef.current = sourceBuffer;
            sourceBuffer.addEventListener("updateend", flushQueue);
            flushQueue();
        }, { once: true });
    }, [clear, flushQueue]);

    const append = useCallback((chunk: ArrayBuffer) => {
        queueRef.current.push(chunk);
        flushQueue();
    }, [flushQueue]);

    const end = useCallback(() => {
        const mediaSource = mediaSourceRef.current;
        const sourceBuffer = sourceBufferRef.current;
        if (!mediaSource || mediaSource.readyState !== "open") {
            return;
        }
        if (sourceBuffer?.updating || queueRef.current.length > 0) {
            return;
        }
        mediaSource.endOfStream();
    }, []);

    useEffect(() => clear, [clear]);

    return {
        start,
        append,
        end,
        clear,
    };
}
